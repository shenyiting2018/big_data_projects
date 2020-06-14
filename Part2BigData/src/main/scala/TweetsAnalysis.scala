import org.apache.spark.SparkConf
import org.apache.spark.streaming.dstream.DStream
import org.apache.spark.streaming.twitter.TwitterUtils
import org.apache.spark.streaming.{Minutes, Seconds, State, StateSpec, StreamingContext}

object TweetsAnalysis {

  def updateTopic(key: String, value: Option[Int], state: State[Int]): (String, Int) = {
    val lastCount: Int =
      state
        .getOption()
        .getOrElse(0)

    val newCount = value.getOrElse(0)

    state.update(newCount)
    (key, newCount - lastCount)
  }

//  def getEmergingTopic(window: DStream[Map[String, Serializable]], spec: StateSpec[String, Int, Int, (String, Int)]): (String) = {
//    var emergingTopic = ""
//    val topics = window.flatMap(t => t("hashtags").asInstanceOf[Array[String]])
//      .map(h => (h, 1))
//      .reduceByKey(_+_)
//      .mapWithState(spec)
//      .map{case (topic, count) => (count, topic)}
//      .transform(_.sortByKey(false)) //sorting as desc
//    topics.foreachRDD(rdd => {
//      val top = rdd.top(1) //rdd.take(1)
//      top.foreach{case (count, topic) => emergingTopic = topic}
//    })
//    return emergingTopic
//  }

  def main(args: Array[String]): Unit = {
    // Parse input argument for accessing twitter streaming api
    if (args.length < 4) {
      System.err.println("Usage: Demo <consumer key> <consumer secret> " + "<access token> <access token secret> [<filters>]")
      System.exit(1)
    }
    val Array(consumerKey, consumerSecret, accessToken, accessTokenSecret) = args.take(4)
    val filters = args.takeRight(args.length - 4)
    // Set the system properties so that Twitter4j library used by twitter stream
    // can use them to generate OAuth credentials
    System.setProperty("twitter4j.oauth.consumerKey", consumerKey)
    System.setProperty("twitter4j.oauth.consumerSecret", consumerSecret)
    System.setProperty("twitter4j.oauth.accessToken", accessToken)
    System.setProperty("twitter4j.oauth.accessTokenSecret", accessTokenSecret)
    val conf = new SparkConf().setAppName("tweetsAnalysis").setMaster("local[*]")
    val ssc = new StreamingContext(conf, Seconds(1))

    //creating twitter input stream
    val tweets = TwitterUtils.createStream(ssc, None, filters)
    //tweets.print()

    //filter the non-English tweets and those with no hashtag
    tweets.foreachRDD { (rdd, time) =>
      rdd.map(t => {
        Map(
          "user" -> t.getUser.getScreenName,
          //"location" -> Option(t.getGeoLocation).map(geo => { s"${geo.getLatitude},${geo.getLongitude}"}),
          "text" -> t.getText,
          "hashtags" -> t.getHashtagEntities.map(_.getText),
          //"retweet" -> t.getRetweetCount,
          "language" -> t.getLang
          //"sentiment" -> SentimentAnalysisUtils.detectSentiment(t.getText).toString
        )
      }).filter(v => {
        val tweetArray = v("hashtags").asInstanceOf[Array[String]]
        v("language").equals("en") && tweetArray.length > 0
      })
    }

      val spec = StateSpec.function(updateTopic _)
      val window = tweets.transform(rdd => {
        rdd.map(t => {
          Map(
            "user"-> t.getUser.getScreenName,
            "text" -> t.getText,
            "hashtags" -> t.getHashtagEntities.map(_.getText),
            "language" -> t.getLang,
            "sentiment" -> SentimentAnalysisUtils.detectSentiment(t.getText).toString)
        })
      }).filter(v => {
        val tweetArray = v("hashtags").asInstanceOf[Array[String]]
        v("language").equals("en") && tweetArray.length > 0
      }).window(Minutes(1), Minutes(1))

      //get the emerging topics
      val topics = window.flatMap(t => t("hashtags").asInstanceOf[Array[String]])
        .map(h => (h, 1))
        .reduceByKey(_+_)
        .mapWithState(spec)
        .map{case (topic, count) => (count, topic)}
        .transform(_.sortByKey(false)) //sorting as desc

      var emergingTopic = ""
      topics.foreachRDD(rdd => {
        val top = rdd.top(1) //rdd.take(1)
        top.foreach{case (count, topic) => emergingTopic = topic}
      })

      //select all tweets related emergingTag
      window.foreachRDD(rdd => {
        println("Emerging topic: %s".format(emergingTopic))
        rdd.filter(t => {
          val tags = t("hashtags").asInstanceOf[Array[String]]
          tags.contains(emergingTopic)
        }).coalesce(1).saveAsTextFile("./result_" + emergingTopic)
      })

    // gotta define a checkpoint directory for mapWithState
    ssc.checkpoint("./checkpoint")
    // Start streaming
    ssc.start()
    // Wait for Termination
    ssc.awaitTermination()
  }
}
