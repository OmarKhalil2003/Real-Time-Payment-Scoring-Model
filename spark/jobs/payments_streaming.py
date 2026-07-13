import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, to_timestamp, current_timestamp,
    year, month, dayofmonth, coalesce,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, DoubleType, IntegerType,
)


def build_spark() -> SparkSession:
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "http://minio:9000")
    minio_access_key = os.getenv("MINIO_ACCESS_KEY", "minio")
    minio_secret_key = os.getenv("MINIO_SECRET_KEY", "minio12345")

    builder = (
        SparkSession.builder.appName("payments_streaming")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .config("spark.hadoop.fs.s3a.endpoint", minio_endpoint)
        .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
        .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config("spark.hadoop.fs.s3a.aws.credentials.provider", "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider")
    )
    return builder.getOrCreate()


def main() -> None:
    kafka_bootstrap = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
    kafka_topic = os.getenv("KAFKA_TOPIC", "payments")

    pg_host = os.getenv("POSTGRES_HOST", "postgres")
    pg_port = os.getenv("POSTGRES_PORT", "5432")
    pg_user = os.getenv("POSTGRES_USER", "postgres")
    pg_password = os.getenv("POSTGRES_PASSWORD", "password")
    pg_db = os.getenv("POSTGRES_DB", "payment_scoring")
    pg_url = f"jdbc:postgresql://{pg_host}:{pg_port}/{pg_db}"

    minio_bucket = os.getenv("MINIO_BUCKET", "payments-lake")
    lake_base = f"s3a://{minio_bucket}"
    checkpoint_base = os.getenv("SPARK_CHECKPOINT", "/tmp/spark_checkpoints")

    spark = build_spark()
    spark.sparkContext.setLogLevel(os.getenv("SPARK_LOG_LEVEL", "WARN"))

    schema = StructType([
        StructField("transaction_id", StringType(), True),
        StructField("customer_id", StringType(), True),
        StructField("merchant_id", StringType(), True),
        StructField("amount", DoubleType(), True),
        StructField("currency", StringType(), True),
        StructField("payment_method", StringType(), True),
        StructField("country", StringType(), True),
        StructField("device", StringType(), True),
        StructField("ip", StringType(), True),
        StructField("event_type", StringType(), True),
        StructField("fraud_label", IntegerType(), True),
        StructField("feature_1", DoubleType(), True),
        StructField("feature_2", DoubleType(), True),
        StructField("feature_3", DoubleType(), True),
        StructField("timestamp", StringType(), True),
    ])

    raw_kafka = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", kafka_bootstrap)
        .option("subscribe", kafka_topic)
        .option("startingOffsets", os.getenv("KAFKA_STARTING_OFFSETS", "latest"))
        .load()
    )

    parsed = raw_kafka.select(
        col("value").cast("string").alias("json_value"),
        col("timestamp").alias("kafka_timestamp"),
    )

    events = (
        parsed.withColumn("data", from_json(col("json_value"), schema))
        .select(
            col("data.transaction_id").alias("transaction_id"),
            col("data.customer_id").alias("customer_id"),
            col("data.merchant_id").alias("merchant_id"),
            col("data.amount").alias("amount"),
            col("data.country").alias("country"),
            col("data.feature_1").alias("feature_1"),
            col("data.feature_2").alias("feature_2"),
            col("data.feature_3").alias("feature_3"),
            col("data.timestamp").alias("event_time_raw"),
            col("kafka_timestamp"),
        )
        .withColumn("event_time", coalesce(to_timestamp("event_time_raw"), col("kafka_timestamp")))
        .filter(col("transaction_id").isNotNull())
        .filter(col("customer_id").isNotNull())
    )

    deduped = (
        events.withWatermark("event_time", os.getenv("WATERMARK", "10 minutes"))
        .dropDuplicates(["transaction_id"])
        .withColumn("ingested_at", current_timestamp())
        .withColumn("year", year(col("event_time")))
        .withColumn("month", month(col("event_time")))
        .withColumn("day", dayofmonth(col("event_time")))
    )

    raw_query = (
        parsed.writeStream.format("parquet")
        .option("path", f"{lake_base}/raw/payments")
        .option("checkpointLocation", f"{checkpoint_base}/raw")
        .outputMode("append")
        .start()
    )

    processed_query = (
        deduped.writeStream.format("delta")
        .option("path", f"{lake_base}/processed/payments")
        .option("checkpointLocation", f"{checkpoint_base}/processed")
        .partitionBy("year", "month", "day")
        .outputMode("append")
        .start()
    )

    curated_query = (
        deduped.select(
            "transaction_id", "customer_id", "merchant_id", "amount",
            "country", "feature_1", "feature_2", "feature_3",
            "event_time", "ingested_at", "year", "month", "day",
        )
        .writeStream.format("delta")
        .option("path", f"{lake_base}/curated/payments")
        .option("checkpointLocation", f"{checkpoint_base}/curated")
        .partitionBy("year", "month", "day")
        .outputMode("append")
        .start()
    )

    def write_to_postgres(batch_df, batch_id: int) -> None:
        if batch_df.isEmpty():
            return
        (
            batch_df.select(
                "transaction_id", "customer_id", "amount", "country",
                "feature_1", "feature_2", "feature_3", "event_time", "ingested_at",
            )
            .write.mode("append")
            .format("jdbc")
            .option("url", pg_url)
            .option("dbtable", "operational_transactions")
            .option("user", pg_user)
            .option("password", pg_password)
            .option("driver", "org.postgresql.Driver")
            .save()
        )

    pg_query = (
        deduped.writeStream.foreachBatch(write_to_postgres)
        .option("checkpointLocation", f"{checkpoint_base}/postgres")
        .outputMode("update")
        .start()
    )

    spark.streams.awaitAnyTermination()


if __name__ == "__main__":
    main()
