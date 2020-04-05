package api

import (
	"html/template"
	"log"
	"net"
	"net/http"
	"strconv"
	"time"

	"github.com/luoruofeng/NewsFMAPI/api/common"
)

type ApiServer struct {
	httpServer *http.Server
}

var (
	G_apiServer *ApiServer
)

func handleShow(resp http.ResponseWriter, r *http.Request) {
	resp.WriteHeader(http.StatusOK)
	resp.Write([]byte("test"))
}

func handleIndex(resp http.ResponseWriter, r *http.Request) {
	var (
		articles []common.Article
		tmp      *template.Template
		err      error
		response []byte
	)
	tmp = template.New("index.html")
	if tmp, err = tmp.ParseFiles(G_config.StaticDir + "/index.html"); err != nil {
		log.Fatal(err)
		goto ERR
	}

	if articles, err = G_articleMrg.GetToday(); err != nil {
		log.Fatal(err)
		goto ERR
	}

	if err = tmp.Execute(resp, articles); err != nil {
		log.Fatal(err)
		goto ERR
	}
	return
ERR:
	if response, err = common.BuildResponse(-1, err.Error(), nil); err != nil {
		resp.Write(response)
	}
}

func handleNewTop10(resp http.ResponseWriter, r *http.Request) {
	var (
		articles []common.Article
		err      error
		response []byte
	)
	if articles, err = G_articleMrg.GetTop10(); err != nil {
		goto ERR
	}

	if response, err = common.BuildResponse(0, "", articles); err != nil {
		goto ERR
	}
	resp.WriteHeader(http.StatusOK)
	resp.Write(response)
	return
ERR:
	if response, err = common.BuildResponse(-1, err.Error(), nil); err != nil {
		resp.Write(response)
	}
}

func handleGetToday(resp http.ResponseWriter, r *http.Request) {
	var (
		articles []common.Article
		err      error
		response []byte
	)
	if articles, err = G_articleMrg.GetToday(); err != nil {
		goto ERR
	}

	if response, err = common.BuildResponse(0, "", articles); err != nil {
		goto ERR
	}
	resp.WriteHeader(http.StatusOK)
	resp.Write(response)
	return
ERR:
	if response, err = common.BuildResponse(-1, err.Error(), nil); err != nil {
		resp.Write(response)
	}
}

func InitApiServer() (err error) {
	var (
		mux           *http.ServeMux
		staticDir     http.Dir
		httpServer    *http.Server
		listener      net.Listener
		staticHandler http.Handler
	)

	//config route
	mux = http.NewServeMux()
	mux.HandleFunc("/api/show", handleShow)
	mux.HandleFunc("/api/top10", handleNewTop10)
	mux.HandleFunc("/api/today", handleGetToday)
	mux.HandleFunc("/api/index", handleIndex)

	//static file
	staticDir = http.Dir(G_config.StaticDir)
	staticHandler = http.FileServer(staticDir)
	mux.Handle("/", http.StripPrefix("/", staticHandler))

	if listener, err = net.Listen("tcp", ":"+strconv.Itoa(G_config.ApiPort)); err != nil {
		return
	}

	//create http server
	httpServer = &http.Server{
		ReadTimeout:  time.Duration(G_config.ReadTimeout) * time.Millisecond,
		WriteTimeout: time.Duration(G_config.WriteTimeout) * time.Millisecond,
		Handler:      mux,
	}

	//single
	G_apiServer = &ApiServer{
		httpServer: httpServer,
	}

	go httpServer.Serve(listener)

	return
}
