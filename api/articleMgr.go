package api

import (
	"context"
	"fmt"
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

	clientOptions = options.Client().SetConnectTimeout(time.Duration(G_config.MongoConnectionTimeout) * time.Millisecond).ApplyURI(G_config.MongoUri)

	if client, err = mongo.Connect(context.TODO(), clientOptions); err != nil {
		return
	}

	G_articleMrg = &ArticleMgr{
		client:            client,
		articleCollection: client.Database("fm").Collection("article"),
	}
	return
}

func (articleMgr *ArticleMgr) GetTop10() (articles []common.Article, err error) {
	var (
		ctx         context.Context
		cursor      *mongo.Cursor
		findOptions *options.FindOptions
		sortOptions *options.FindOptions
	)
	if err = articleMgr.client.Ping(nil, nil); err != nil {
		fmt.Println(err)
	}

	ctx, _ = context.WithTimeout(context.Background(), time.Duration(30)*time.Second)
	// if cursor, err = articleMgr.articleCollection.Find(ctx, bson.D{{"foo", "bar"}, {"hello", "world"}}); err != nil {

	findOptions = options.Find().SetLimit(10)
	sortOptions = options.Find().SetSort(bson.M{"time": -1})

	if cursor, err = articleMgr.articleCollection.Find(ctx, bson.D{}, findOptions, sortOptions); err != nil {
		log.Fatal(err)
		return
	}
	defer cursor.Close(ctx)
	articles = make([]common.Article, 0)
	for cursor.Next(ctx) {
		//可以使用bson.M或struct做反序列化
		// var m bson.M
		var result common.Article

		if err = cursor.Decode(&result); err != nil {
			log.Fatal(err)
		}
		//可以使用bson.M
		// if err = cursor.Decode(&m); err != nil {
		// 	log.Fatal(err)
		// }

		articles = append(articles, result)
	}
	return
}

func (articleMgr *ArticleMgr) GetToday() (articles []common.Article, err error) {
	var (
		ctx       context.Context
		cursor    *mongo.Cursor
		startTime time.Time
		year      int
		month     time.Month
		day       int
	)
	if err = articleMgr.client.Ping(nil, nil); err != nil {
		fmt.Println(err)
	}

	ctx, _ = context.WithTimeout(context.Background(), time.Duration(30)*time.Second)
	// if cursor, err = articleMgr.articleCollection.Find(ctx, bson.D{{"foo", "bar"}, {"hello", "world"}}); err != nil {

	year, month, day = time.Now().Date()
	startTime = time.Date(year, month, day, 0, 0, 0, 0, time.Local)

	if cursor, err = articleMgr.articleCollection.Find(ctx, bson.D{{"time", bson.D{{"$gte", startTime.Unix()}}}}); err != nil {
		log.Fatal(err)
		return
	}
	defer cursor.Close(ctx)
	articles = make([]common.Article, 0)
	for cursor.Next(ctx) {
		//可以使用bson.M或struct做反序列化
		// var m bson.M
		var result common.Article

		if err = cursor.Decode(&result); err != nil {
			log.Fatal(err)
		}
		//可以使用bson.M
		// if err = cursor.Decode(&m); err != nil {
		// 	log.Fatal(err)
		// }

		articles = append(articles, result)
	}
	return
}
