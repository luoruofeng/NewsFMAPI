package main

import (
	"fmt"
	"time"

	"github.com/luoruofeng/NewsFMAPI/api"
)

func main() {
	var (
		err error
	)
	if err = api.InitApiServer(); err != nil {
		goto ERR
	}

	for {
		time.Sleep(2 * time.Second)
	}
ERR:
	fmt.Println(err)
}
