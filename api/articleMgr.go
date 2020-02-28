package api

import (
	"context"
	"log"
	"time"

	"github.com/luoruofeng/NewsFMAPI/api/common"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo"
	"go.mongodb.org/mongo-driver/mongo/options"
)

type ArticleMgr struct {
	client            *mongo.Client
	articleCollection *mongo.Collection
}

var (
	G_articleMrg *ArticleMgr
)

func InitArticleMgr() (err error) {
	var (
		client        *mongo.Client
		clientOptions *options.ClientOptions
	)

	clientOptions = options.Client().SetConnectTimeout(time.Duration(G_config.MongoConnectionTimeout)).ApplyURI(G_config.MongoUri)

	if client, err = mongo.Connect(context.TODO(), clientOptions); err != nil {
		return
	}

	G_articleMrg = &ArticleMgr{
		client:            client,
		articleCollection: client.Database("fm").Collection("article"),
	}
	return
}

func (articleMgr *ArticleMgr) GetTop50() (articles []common.Article) {
	var (
		ctx        context.Context
		cancelFunc context.CancelFunc
		cursor     *mongo.Cursor
		err        error
	)

	ctx, cancelFunc = context.WithTimeout(context.Background(), time.Duration(30)*time.Second)
	if cursor, err = articleMgr.articleCollection.Find(ctx, bson.D{{"foo", "bar"}, {"hello", "world"}}); err != nil {
		log.Fatal(err)
		return
	}
	defer cursor.Close(ctx)
	articles = make([]common.Article, 1)
	for cursor.Next(ctx) {
		// var result bson.M
		var result common.Article

		if err = cursor.Decode(&result); err != nil {
			log.Fatal(err)
		}
		articles = append(articles, result)
	}
	return
}
