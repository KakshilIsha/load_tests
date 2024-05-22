package main

import (
    "github.com/gin-gonic/gin"
    "strconv"
)

type User struct {
    ID          int    `json:"id"`
    Name        string `json:"name"`
    Description string `json:"description"`
}

func main() {
    gin.SetMode(gin.ReleaseMode)   // Set Gin to release mode to suppress debug and color output
    gin.DisableConsoleColor()      // Optional: disable color output

    r := gin.Default() // Create a router with default middleware: logger and recovery (crash-free) middleware

    r.GET("/users", func(c *gin.Context) {
        var users []User
        for i := 0; i < 100; i++ {
            user := User{
                ID:          i,
                Name:        "User " + strconv.Itoa(i),
                Description: "Description " + strconv.Itoa(i),
            }
            users = append(users, user)
        }
        c.JSON(200, users) // Respond with JSON containing the list of users
    })

    r.Run() // Run the server on default port 8080
}
