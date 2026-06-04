package main

import (
	"fmt"
	"net/http"
	"os"
)

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	apiKey := os.Getenv("API_KEY")
	dbURL := os.Getenv("DATABASE_URL")

	fmt.Printf("Starting server on port %s\n", port)
	fmt.Printf("API Key set: %v\n", apiKey != "")
	fmt.Printf("DB URL set: %v\n", dbURL != "")

	http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		fmt.Fprintln(w, "Hello, World!")
	})

	http.ListenAndServe(":"+port, nil)
}
