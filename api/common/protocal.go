package common

import (
	"encoding/json"

	"go.mongodb.org/mongo-driver/bson/primitive"
)

//文章
type Article struct {
	//id不能写json，写了后，反序列化就会为n个0，也就是空
	Id       primitive.ObjectID `bson:"_id"`
	Time     string             `json:time bson:time`
	Url      string             `json:url bson:url`
	Type     int64              `json:type bson:type`
	Title    string             `json:title bson:title`
	Original int64              `json:original bson:original`
	Content  string             `json:content bson:content`
	NoVoice  bool               `json:no_voice bson:no_voice`
}

//Response
type Response struct {
	ErrorNum int         `json:errnum`
	Message  string      `json:message`
	Data     interface{} `json:data`
}

func BuildResponse(errNO int, message string, data interface{}) (resp []byte, err error) {
	var (
		response Response
	)
	response.ErrorNum = errNO
	response.Message = message
	response.Data = data

	resp, err = json.Marshal(response)
	return
}
