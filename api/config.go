package api

import (
	"encoding/json"
	"io/ioutil"
)

type Config struct {
	ApiPort                int    `json:"apiPort"`
	ReadTimeout            int    `json:"readTimeout"`
	WriteTimeout           int    `json:"writeTimeout"`
	StaticDir              string `json:"staticDir"`
	MongoUri               string `json:"mongoUri"`
	MongoConnectionTimeout int    `json:"mongoConnectionTimeout"`
}

var (
	//single
	G_config *Config
)

func InitConfig(filename string) (err error) {
	var (
		content []byte
		conf    Config
	)

	//read configuration file
	if content, err = ioutil.ReadFile(filename); err != nil {
		return
	}

	//unserialise json
	if json.Unmarshal(content, &conf); err != nil {
		return
	}

	G_config = &conf

	return
}
