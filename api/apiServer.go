package api

import (
	"net"
	"net/http"
	"time"
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

	//static file
	staticDir = http.Dir("")
	staticHandler = http.FileServer(staticDir)
	mux.Handle("/", http.StripPrefix("/", staticHandler))

	if listener, err = net.Listen("tcp", ":"+"8888"); err != nil {
		return
	}

	//create http server
	httpServer = &http.Server{
		ReadTimeout:  time.Duration(5) * time.Millisecond,
		WriteTimeout: time.Duration(5) * time.Millisecond,
		Handler:      mux,
	}

	//single
	G_apiServer = &ApiServer{
		httpServer: httpServer,
	}

	go httpServer.Serve(listener)

	return
}
