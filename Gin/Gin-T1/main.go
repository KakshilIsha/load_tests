package main

import (
	"context"
	"log"
	"net/http"
	"sync"

	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
	jsoniter "github.com/json-iterator/go"
)

var (
	redisClient *redis.Client
	once        sync.Once
	ctx         = context.Background()
	json        = jsoniter.ConfigFastest
)

// Initialize Redis connection pool once during startup
func initRedis() {
	once.Do(func() {
		redisClient = redis.NewClient(&redis.Options{
			Addr:     "3.110.66.116:6379",
			Password: "", // No password set
			DB:       0,  // use default DB
			PoolSize: 100, // Max connections
		})
	})
}

// Handle Redis connection shutdown
func closeRedis() {
	if err := redisClient.Close(); err != nil {
		log.Println("Error closing Redis connection:", err)
	}
}

// Handler for the /test1 endpoint
func getValueFromRedis(c *gin.Context) {

	value, err := redisClient.Get(ctx, "TestJSON").Result()
	if err != nil {
		c.JSON(http.StatusOK, gin.H{"data": nil})
		return
	}

	var valueDict map[string]interface{}
	if err := json.UnmarshalFromString(value, &valueDict); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse JSON"})
		return
	}

	// Optimized loop to replace 'default_value' keys
	if data, ok := valueDict["data"].(map[string]interface{}); ok {
		if stepData, ok := data["step_data"].(map[string]interface{}); ok {
			if pages, ok := stepData["pages"].([]interface{}); ok {
				for _, page := range pages {
					if pageMap, ok := page.(map[string]interface{}); ok {
						if sectionsList, ok := pageMap["sections_list"].([]interface{}); ok {
							for _, section := range sectionsList {
								if sectionMap, ok := section.(map[string]interface{}); ok {
									if fieldsList, ok := sectionMap["fields_list"].([]interface{}); ok {
										for _, field := range fieldsList {
											if fieldMap, ok := field.(map[string]interface{}); ok {
												if key, ok := fieldMap["key"]; ok {
													fieldMap["default_value"] = key
												} else {
													fieldMap["default_value"] = nil
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}

	c.JSON(http.StatusOK, gin.H{"data": valueDict})
}

func main() {
	// Set up Gin router
	r := gin.Default()
	initRedis() // Ensure Redis is initialized

	// Route for /test1
	r.GET("/test1", getValueFromRedis)

	// Start server on port 9000
	if err := r.Run(":9000"); err != nil {
		log.Fatal("Failed to start server:", err)
	}

	// Close Redis connection when shutting down
	defer closeRedis()
}
