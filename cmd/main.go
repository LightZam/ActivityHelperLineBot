package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"os/exec"

	"github.com/line/line-bot-sdk-go/linebot"
)

var bot *linebot.Client

// TaishinEvent store taishin activities information
type TaishinEvent struct {
	Title       string `json:"title"`
	Description string `json:"desc"`
}

func initLineBot() {
	var err error
	bot, err = linebot.New(
		os.Getenv("ChannelSecret"),
		os.Getenv("ChannelAccessToken"),
	)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	initLineBot()
	// Listen to the root path of the web app
	http.HandleFunc("/", handler)
	// handle bot
	http.HandleFunc("/callback", handleEvents)

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

func handleEvents(writer http.ResponseWriter, request *http.Request) {
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
		fmt.Println("fmt event Source: ", event.Source)
		if event.Type == linebot.EventTypeMessage {
			userID := event.Source.UserID
			groupID := event.Source.GroupID
			roomID := event.Source.RoomID

			fmt.Println("userID", userID, "groupID", groupID, "roomID", roomID)
			switch message := event.Message.(type) {
			case *linebot.TextMessage:
				handleText(message, event.ReplyToken)
			}
		}
	}
}

func handleText(message *linebot.TextMessage, replyToken string) {
	registerTaishinActivities(message, replyToken)
	// if message.Text == "註冊" {
	// }

	// if message.Text == "活動" {

	// }
}

func registerTaishinActivities(message *linebot.TextMessage, replyToken string) {
	out, err := exec.Command("python", "ActivityHelper.py", "get", "-u", message.Text).Output()

	if err != nil {
		fmt.Println(err.Error())
		// 	_, err := bot.ReplyMessage(replyToken, linebot.NewTextMessage("py err")).Do()
		// 	if err != nil {
		// 		fmt.Println("fail to send message")
		// 	}
	} else {
		var events []TaishinEvent
		json.Unmarshal(out, &events)
		fmt.Println(events)
		// fmt.Println(events[0].Title)
		// fmt.Println(events[0].Description)
		_, err := bot.ReplyMessage(replyToken, linebot.NewTextMessage(events[0].Title)).Do()
		if err != nil {
			fmt.Println("fail to send message")
		}
	}
}
