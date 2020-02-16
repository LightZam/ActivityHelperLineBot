package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
)

func main() {
	// Listen to the root path of the web app
	http.HandleFunc("/", handler)

	http.HandleFunc("/taishin", registerTaishinActivities)

	// Start a web server.
	// http.ListenAndServe(":8080", nil)
	http.ListenAndServe(":"+os.Getenv("PORT"), nil)
}

// The handler for the root path.
func handler(writer http.ResponseWriter, request *http.Request) {
	fmt.Fprintf(writer, "This is the service for Activity Helper. by Zam")
}

// User store information for Taishin bank
type User struct {
	ID string `json:"id"`
}

func registerTaishinActivities(writer http.ResponseWriter, request *http.Request) {
	body, _ := ioutil.ReadAll(request.Body)
	defer request.Body.Close()
	fmt.Println(body)
	writer.Write(body)

	// var user User
	// json.Unmarshal(body, &user)
	// writer.Write([]byte(user.ID))
}
