package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/line/line-bot-sdk-go/linebot"
)

var bot *linebot.Client

func main() {
	// Listen to the root path of the web app
	http.HandleFunc("/", handler)

	http.HandleFunc("/taishin", registerTaishinActivities)
	var err error
	bot, err = linebot.New(
		os.Getenv("ChannelSecret"),
		os.Getenv("ChannelAccessToken"),
	)
	if err != nil {
		log.Fatal(err)
	}

	fmt.Println("fmt os env: ", os.Getenv("ChannelSecret"), os.Getenv("ChannelAccessToken"), os.Getenv("PORT"))
	log.Print("log os env: ", os.Getenv("ChannelSecret"), os.Getenv("ChannelAccessToken"), os.Getenv("PORT"))

	if err := http.ListenAndServe(":"+os.Getenv("PORT"), nil); err != nil {
		log.Fatal(err)
	}
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
	// body, _ := ioutil.ReadAll(request.Body)
	// defer request.Body.Close()
	// fmt.Println(body)
	// writer.Write(body)

	// var user User
	// json.Unmarshal(body, &user)
	// writer.Write([]byte(user.ID))

	events, err := bot.ParseRequest(request)
	if err != nil {
		if err == linebot.ErrInvalidSignature {
			writer.WriteHeader(400)
		} else {
			writer.WriteHeader(500)
		}
		return
	}
	for _, event := range events {
		fmt.Println("fmt event: ", event)
		log.Print("log event: ", event)
		if event.Type == linebot.EventTypeMessage {
			switch message := event.Message.(type) {
			case *linebot.TextMessage:
				if _, err = bot.ReplyMessage(event.ReplyToken, linebot.NewTextMessage(message.Text)).Do(); err != nil {
					log.Print(err)
				}
			}
		}
	}
}
