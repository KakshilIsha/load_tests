package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v4/pgxpool"
)

var db *pgxpool.Pool

const (
	staticUsername = "isha"
	staticPassword = "password"
	databaseURL    = "postgresql://postgres:ishapostgres@52.66.234.102:5432/postgres"
)

func main() {
	// Create a new Gin router
	r := gin.Default()

	// Initialize database connection pool
	var err error
	db, err = InitDatabase()
	if err != nil {
		log.Fatalf("Unable to initialize database: %v\n", err)
		os.Exit(1)
	}
	defer db.Close()

	// POST route for /test3
	r.POST("/test3/", submitData)

	// Start server
	r.Run(":9000") // Start the server on port 9000
}

// Initialize the database pool with custom connection pool size
func InitDatabase() (*pgxpool.Pool, error) {
	dbUrl := databaseURL
	config, err := pgxpool.ParseConfig(dbUrl)
	if err != nil {
		return nil, fmt.Errorf("failed to parse config: %w", err)
	}

	// Set connection pool size
	config.MaxConns = 100
	config.MinConns = 50

	dbPool, err := pgxpool.ConnectConfig(context.Background(), config)
	if err != nil {
		return nil, fmt.Errorf("failed to create pool: %w", err)
	}
	return dbPool, nil
}

// Calculate the average of col9 from the read_table
func calculateAverageCol9(conn *pgxpool.Conn) (float64, error) {
	query := `
    SELECT AVG(col9) AS avg_col9
    FROM read_table
    LIMIT 1000;
    `
	var avgCol9 float64
	err := conn.QueryRow(context.Background(), query).Scan(&avgCol9)
	if err != nil {
		return 0, err
	}
	return avgCol9, nil
}

// Handler function for /test3 route
func submitData(c *gin.Context) {
	// Parse input data
	var data map[string]string
	if err := c.ShouldBindJSON(&data); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request data"})
		return
	}

	username := data["username"]
	password := data["password"]

	// Static validation for username and password
	if username != staticUsername || password != staticPassword {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	conn, err := db.Acquire(context.Background())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to acquire database connection"})
		return
	}
	defer conn.Release()

	// Calculate the average of col9
	averageCol9, err := calculateAverageCol9(conn)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to calculate average"})
		return
	}

	// Fetch one row of example data
	readQuery := `
    SELECT col1, col2, col3, col4, col5, col10, col2, col3, col15::jsonb
    FROM read_table
    LIMIT 1;
    `
	var col1, col4, col10 string
	var col2 int
	var col3 float64
	var col5 bool
	var col15 json.RawMessage

	err = conn.QueryRow(context.Background(), readQuery).Scan(&col1, &col2, &col3, &col4, &col5, &col10, &col2, &col3, &col15)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch row"})
		return
	}

	// Insert into write_table using prepared statement
	writeQuery := `
    INSERT INTO write_table (col1, col2, col3, col4, col5, col6, col7, col8, col9, col10)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    RETURNING id;
    `
	_, err = conn.Exec(context.Background(), writeQuery, col1, col2, col3, col4, col5, col10, col2, col3, fmt.Sprintf("%f", averageCol9), col15)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to insert data"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Success", "status": "ok"})
}
