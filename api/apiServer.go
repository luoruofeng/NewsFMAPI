package api

import (
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
