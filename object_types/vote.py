# Votes are placed by players, and are read in by the bot update.
# Votes have a voter, a target, a link to the post, and a post number.

class vote:
  def __init__(self, voter, target, url, postnum, game):
    self.voter = voter
    self.target = target
    self.url = url
    self.postnum = postnum
    self.game = game