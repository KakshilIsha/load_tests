package main

import (
	"context"
	"log"
	"net/http"
	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v5/pgxpool"
)

var db *pgxpool.Pool

func initDB() error {
	connString := "postgres://odoo:odoo@localhost:5432/odooDb15" // Adjust as necessary
	config, err := pgxpool.ParseConfig(connString)
	if err != nil {
		return err
	}
	config.MaxConns = 50
	config.MinConns = 5

	pool, err := pgxpool.NewWithConfig(context.Background(), config)
	if err != nil {
		return err
	}
	db = pool
	return nil
}

func main() {
	err := initDB()
	if err != nil {
		log.Fatalf("Failed to initialize DB: %v", err)
	}
	defer db.Close()

	r := gin.Default()
	r.POST("/users", readUsersPost)
	r.Run(":8080") // listen and serve on 0.0.0.0:8080
}

func readUsersPost(c *gin.Context) {
	var params map[string]interface{}
	if err := c.ShouldBindJSON(&params); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid JSON"})
		return
	}

	limit, ok := params["limit"].(float64)
	if !ok {
		limit = 100 // Default limit
	}

	// Print the params
	log.Println(params)

	// Construct the SQL query using the parameters
	query := "SELECT * FROM load_test LIMIT $1"

	rows, err := db.Query(context.Background(), query, int(limit))
	if err != nil {
		log.Printf("Error querying database: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error querying database", "details": err.Error()})
		return
	}
	defer rows.Close()

	var users []map[string]interface{}
	for rows.Next() {
		values, err := rows.Values()
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Error reading rows"})
			return
		}

		user := make(map[string]interface{})
		fieldDescriptions := rows.FieldDescriptions()
		for i, val := range values {
			user[string(fieldDescriptions[i].Name)] = val
		}

		users = append(users, user)
	}

	if rows.Err() != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error iterating rows"})
		return
	}

	c.JSON(http.StatusOK, users)
}
