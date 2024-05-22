package main

import (
	"context"
	"log"
	"math/rand"
	"net/http"
	"time"

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
	r.GET("/users", getUser)
	r.Run(":8080") // listen and serve on 0.0.0.0:8080
}

func getUser(c *gin.Context) {
	rand.Seed(time.Now().UnixNano()) // Seed the random number generator
	randomID := rand.Intn(600000) + 1 // Generate a random ID between 1 and 600000

	var id int
	var name, description string

	err := db.QueryRow(context.Background(), "SELECT id, name, description FROM load_test WHERE id = $1", randomID).Scan(&id, &name, &description)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Error querying database"})
		return
	}

	user := map[string]interface{}{
		"id":          id,
		"name":        name,
		"description": description,
	}

	c.JSON(http.StatusOK, user)
}
