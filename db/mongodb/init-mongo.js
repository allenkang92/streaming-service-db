db = db.getSiblingDB('streaming_analytics');

// Create collections with schema validation
db.createCollection("viewing_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["user_id", "episode_id", "timestamp", "action", "device_info"],
            properties: {
                user_id: { bsonType: "int" },
                episode_id: { bsonType: "int" },
                timestamp: { bsonType: "date" },
                action: { enum: ["play", "pause", "stop", "seek"] },
                device_info: { bsonType: "object" },
                streaming_quality: { bsonType: "object" }
            }
        }
    }
});

db.createCollection("user_behaviors", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["user_id", "action_type", "timestamp"],
            properties: {
                user_id: { bsonType: "int" },
                action_type: { enum: ["search", "browse", "rate", "bookmark", "share"] },
                timestamp: { bsonType: "date" },
                details: { bsonType: "object" }
            }
        }
    }
});

db.createCollection("performance_metrics", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["timestamp", "metric_type", "value"],
            properties: {
                timestamp: { bsonType: "date" },
                metric_type: { enum: ["cdn_latency", "server_load", "streaming_quality", "error_rate"] },
                value: { bsonType: "double" },
                details: { bsonType: "object" }
            }
        }
    }
});

db.createCollection("error_logs", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["timestamp", "error_type", "severity", "message"],
            properties: {
                timestamp: { bsonType: "date" },
                error_type: { bsonType: "string" },
                severity: { enum: ["low", "medium", "high", "critical"] },
                message: { bsonType: "string" },
                stack_trace: { bsonType: "string" }
            }
        }
    }
});
