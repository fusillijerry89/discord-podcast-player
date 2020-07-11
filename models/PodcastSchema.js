const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const CommentSchema = require('./CommentSchema');

const PodcastSchema = new Schema({
  title: {
    type: String,
    required: true,
    unique: true
  },
  comments: {
    type : Schema.Types.ObjectId,
    ref : 'CommentSchema'
  },
  tags: {
    type: [String],
    required: false
  }
});

module.exports = mongoose.model('Podcast', PodcastSchema);
