package main

import (
	"context"
	"log"
	"net/http"
	"sync"

	"github.com/bytedance/sonic"
	"github.com/gin-gonic/gin"
	"github.com/go-redis/redis/v8"
)

var (
	redisClient *redis.Client
	once        sync.Once
	ctx         = context.Background()
)

type Page struct {
	PageType           string    `json:"page_type"`
	Title              string    `json:"title"`
	ShouldDisplayTitle bool      `json:"should_display_title"`
	PageNumber         int       `json:"page_number"`
	SubTitle           string    `json:"sub_title"`
	PreSectionMessage  string    `json:"pre_section_message"`
	PostSectionMessage string    `json:"post_section_message"`
	SectionsList       []Section `json:"sections_list"`
}

type Section struct {
	Title               string        `json:"title"`
	ShouldDisplayTitle  bool          `json:"should_display_title"`
	SectionDisplayOrder int           `json:"section_display_order"`
	SubTitle            bool          `json:"sub_title"`
	IsReplicable        bool          `json:"is_replicable"`
	FieldsList          []Field       `json:"fields_list"`
	GroupsList          []interface{} `json:"groups_list"`
	ID                  int           `json:"id"`
}

type Field struct {
	Key                string        `json:"key"`
	Title              string        `json:"title"`
	PlaceholderText    string        `json:"placeholder_text"`
	DefaultValue       string        `json:"default_value"`
	HelperText         string        `json:"helper_text"`
	ShouldCallAPI      bool          `json:"should_call_api"`
	IsMarketingTracked bool          `json:"is_marketing_tracked"`
	DisplayOrder       int           `json:"display_order"`
	Prefix             string        `json:"prefix"`
	Suffix             string        `json:"suffix"`
	Comments           string        `json:"comments"`
	ShouldDisplay      bool          `json:"should_display"`
	ShouldDisplayTitle bool          `json:"should_display_title"`
	Type               string        `json:"type"`
	Choices            []Choice      `json:"choices"`
	DisplayConditions  []interface{} `json:"display_conditions"`
	Validation         any           `json:"validation"`
	SectionID          int           `json:"section_id"`
}

type Choice struct {
	DisplayTitle string `json:"display_title"`
	DisplayOrder int    `json:"display_order"`
	Value        any    `json:"value"`
}

type Validation struct {
	Name         string `json:"name"`
	Regex        string `json:"regex"`
	ErrorMessage string `json:"error_message"`
	Required     bool   `json:"required"`
	MinLength    int    `json:"min_length"`
	MaxLength    int    `json:"max_length"`
}

type StepData struct {
	FormID             int        `json:"form_id"`
	AvailableLanguages []Language `json:"available_languages"`
	Title              string     `json:"title"`
	Description        string     `json:"description"`
	ActionURL          string     `json:"action_url"`
	ActionMethod       string     `json:"action_method"`
	Pages              []Page     `json:"pages"`
}

type Language struct {
	DisplayTitle string `json:"display_title"`
	Value        string `json:"value"`
}

type Data struct {
	StepData StepData `json:"step_data"`
	StepID   any      `json:"step_id"`
}

type Response struct {
	Msg   string `json:"msg"`
	MsgID string `json:"msgid"`
	Data  Data   `json:"data"`
}

// Initialize Redis connection pool once during startup
func initRedis() {
	once.Do(func() {
		redisClient = redis.NewClient(&redis.Options{
			Addr:     "3.110.140.138:6379",
			Password: "",  // No password set
			DB:       0,   // use default DB
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

	var valueDict Response
	if err := sonic.UnmarshalString(value, &valueDict); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to parse JSON"})
		return
	}

	for i, page := range valueDict.Data.StepData.Pages {
		for j, section := range page.SectionsList {
			for k, field := range section.FieldsList {
				// Replace the default_value with the key value
				valueDict.Data.StepData.Pages[i].SectionsList[j].FieldsList[k].DefaultValue = field.Key
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
