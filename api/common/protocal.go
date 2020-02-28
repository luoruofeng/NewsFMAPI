package common

//文章
type Article struct {
	Time     string `json:time bson:time`
	Url      string `json:url bson:url`
	Type     string `json:type bson:type`
	Title    string `json:title bson:title`
	Original int64  `json:original bson:original`
	Content  string `json:content bson:content`
	NoVoice  bool   `json:no_voice bson:no_voice`
}

// article过滤条件
type ArticleFilter struct {
	NoVoice bool `bson:"no_voice"`
}

// article过滤条件
type ArticleTimeFilter struct {
	Time string `bson:time`
}

// article排序规则
type SortArticleByTime struct {
	SortOrder int `bson:"time"` // {time: -1}
}
