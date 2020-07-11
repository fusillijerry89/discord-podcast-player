const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const CommentSchema = new Schema({
  podcast_title: {
    type: String,
    required: true,
    unique: true
  },
  comment_body: String,
  user: String,
  time: String,
  channel: String,
  server: String
});

module.exports = mongoose.model('Comment', CommentSchema);
