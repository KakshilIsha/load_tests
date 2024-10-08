package main

import (
	"context"
	"encoding/json"
	"fmt"
	"math/rand"
	"net/http"
	"os"
	"strconv"
	"time"

	"github.com/bytedance/sonic"
	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v4/pgxpool"
)

// Global PostgreSQL connection pool
var pool *pgxpool.Pool

type ColumnData struct {
	Key1  string `json:"Key1"`
	Key2  string `json:"Key2"`
	Key3  string `json:"Key3"`
	Key4  string `json:"Key4"`
	Key5  string `json:"Key5"`
	Key6  string `json:"Key6"`
	Key7  string `json:"Key7"`
	Key8  string `json:"Key8"`
	Key9  string `json:"Key9"`
	Key10 string `json:"Key10"`
	Key11 string `json:"Key11"`
	Key12 string `json:"Key12"`
	Key13 string `json:"Key13"`
	Key14 string `json:"Key14"`
	Key15 string `json:"Key15"`
	Key16 string `json:"Key16"`
	Key17 string `json:"Key17"`
	Key18 string `json:"Key18"`
	Key19 string `json:"Key19"`
	Key20 string `json:"Key20"`
	Key21 string `json:"Key21"`
	Key22 string `json:"Key22"`
	Key23 string `json:"Key23"`
	Key24 string `json:"Key24"`
	Key25 string `json:"Key25"`
	Key26 string `json:"Key26"`
	Key27 string `json:"Key27"`
	Key28 string `json:"Key28"`
	Key29 string `json:"Key29"`
	Key30 string `json:"Key30"`
}

// InitDatabase initializes the connection pool for PostgreSQL
func InitDatabase() (*pgxpool.Pool, error) {
	dbUrl := "postgresql://postgres:ishapostgres@3.110.140.138:5432/postgres"
	config, err := pgxpool.ParseConfig(dbUrl)
	if err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	// Set connection pool size
	config.MaxConns = 50
	config.MinConns = 20

	dbPool, err := pgxpool.ConnectConfig(context.Background(), config)
	if err != nil {
		return nil, fmt.Errorf("failed to create pool: %w", err)
	}
	return dbPool, nil
}

func main() {
	// Initialize database connection pool
	var err error
	pool, err = InitDatabase()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Unable to connect to database: %v\n", err)
		os.Exit(1)
	}
	defer pool.Close()

	// Set up the Gin router with optimized settings
	router := gin.New()
	router.Use(gin.Recovery())

	// Define the route and the handler
	router.GET("/test2", queryData)

	// Start the Gin server using the default `net/http` server
	if err := router.Run(":9000"); err != nil {
		fmt.Fprintf(os.Stderr, "Server failed to start: %v\n", err)
	}
}

// QueryData fetches data from the database and returns it
func queryData(c *gin.Context) {
	// Get the 'value' query parameter
	valueStr := c.Query("value")
	value, err := strconv.Atoi(valueStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid 'value' parameter"})
		return
	}

	// SQL query
	query := `
	SELECT id, col1, col2, col3, col4, col5, col6, col7, col8, col9, col10, col11, col12, col13, col14, col15
	FROM read_table
	WHERE col2 < $1
	LIMIT 100;
	`

	// Execute the query
	rows, err := pool.Query(context.Background(), query, value)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	// Prepare the result
	var result []map[string]interface{}
	for rows.Next() {
		var (
			id    int
			col1  string
			col2  int
			col3  float64
			col4  string
			col5  bool
			col6  time.Time
			col7  time.Time
			col8  string
			col9  int
			col10 string
			col11 string
			col12 string
			col13 float64
			col14 string
			col15 []byte // JSONB type in Go is typically handled as []byte or json.RawMessage
		)

		err := rows.Scan(
			&id, &col1, &col2, &col3, &col4, &col5, &col6, &col7, &col8, &col9, &col10, &col11,
			&col12, &col13, &col14, &col15,
		)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": fmt.Sprintf("Scan error: %v", err)})
			return
		}

		// Parse col15 (assuming it's JSON) using fastjson
		var col15Data ColumnData
		err = sonic.Unmarshal(col15, &col15Data)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error parsing col15"})
			return
		}

		// Update the deserialized JSON
		col15Data.Key1 = "ModifiedData"
\

		// Append to result with modified values
		rowMap := map[string]interface{}{
			"id":    id,
			"col1":  col1,
			"col2":  rand.Intn(1000), // Modify col2 value
			"col3":  col3,
			"col4":  col4,
			"col5":  col5,
			"col6":  col6,
			"col7":  col7,
			"col8":  col8,
			"col9":  col9,
			"col10": col10,
			"col11": col11,
			"col12": col12,
			"col13": col13,
			"col14": col14,
			"col15": col15Data, // Assign the modified JSON
		}
		result = append(result, rowMap)
	}

	// Return the result as JSON
	c.JSON(http.StatusOK, gin.H{"data": result})
}
