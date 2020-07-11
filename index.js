const express = require('express');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');

const app = express();
var jsonParser = bodyParser.json();
var urlEncodedParser = bodyParser.urlencoded({ extended: true });


app.set('view engine', 'ejs');

app.use(bodyParser.urlencoded({ extended: false }));

// Connect to MongoDB
mongoose
  .connect(
    'mongodb://mongo:27017/docker-node-mongo',
    { useNewUrlParser: true }
  )
  .then(() => console.log('MongoDB Connected'))
  .catch(err => console.log(err));

const PodcastSchma = require('./models/PodcastSchema');
const CommentSchema = require('./models/CommentSchema');

app.get('/', (req, res) => {
  res.send("Hello");
});

app.get('/podcasts', (req, res) => {
  PodcastSchma.find()
    .then(podcasts => res.send(podcasts));
});

app.get('/podcast/bytitle/:title', (req, res) => {
  PodcastSchma.findOne({ title : req.params.title })
    .then(podcast => res.send(podcast));
});

app.post('/podcast/add', (req, res) => {
  let title = req.body.title;
  let tags = req.body.tags;

  const newPodcast = new PodcastSchma({
    title : title,
    tags : tags,
    comments : new CommentSchema({
      title : title
    })
  });

  newPodcast.save().then(user => res.redirect('/'));
});

app.post('/comment/:podcast_title', (req, res) => {
  let podcast_title = req.params.podcast_title;
  let comment_body = req.body.comment_body,
    user = req.body.user,
    time = req.body.time,
    channel = req.body.channel,
    server = req.body.server;

  let newComment = new CommentSchema({
    podcast_title : podcast_title,
    comment_body : comment_body,
    user : user,
    time : time,
    channel : channel,
    server : server
  });

  newComment.save().then(user => res.send('Saved comment with title: ' + podcast_title));
});

app.get('/comments', (req, res) => {
  CommentSchema.find()
    .then(comments => res.send(comments));
});

app.get('/comments/:podcast_title', (req, res) => {
  CommentSchema.findOne({ podcast_title : req.params.podcast_title })
    .then(comment => res.send(comment));
});

app.put('/bookmark', urlEncodedParser, (req, res, next) => {
  Bookmark.findOne({ 'url' : req.body.url }, {}, function (err, bookmark) {

    tags = bookmark.tags;
    tags.push(req.body.tags);

    Bookmark.findOneAndUpdate(
      { 'url' : req.body.url },
      { 'tags' : tags },
      { new : true },
      function (err, bookmark)
      {
        if (err) return console.log(err);
        console.log(bookmark);
        res.send(bookmark);
      });
  });
});

app.delete('/bookmark', (req, res) => {
  Bookmark.deleteOne({ 'url': req.body.url })
    .then(bookmark => res.send("Deleted bookmark " + req.body.url));
});

app.delete('/bookmarks', (req, res, err) => {
  Bookmark.deleteMany({})
    .catch(err => {
      res.send(501);
    })
    .then(bookmarks => {
      res.send("Deleted all bookmarks.");
    });
});

const port = 6969;
app.listen(port, () => console.log('Server running...'));
