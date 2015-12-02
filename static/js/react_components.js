function getURLPathArgByPosition(position) {
    // Default to getting the userID from the url
    var pathArray = window.location.pathname.split( '/' );
    return pathArray[position];
}

function getUserFromPropsOrURL(props, position){
    // Get the user id, default from url path
    var userID;
    if (props.userID) {
        userID = props.userID;
    } else {
        userID = getURLPathArgByPosition(position);
    }
    return userID;
}

function getURLParameterByName(name) {
    name = name.replace(/[\[]/, "\\[").replace(/[\]]/, "\\]");
    var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
        results = regex.exec(location.search);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function getElementValueOrNull(elementID){
    if (document.getElementById(elementID) != null) {
        return document.getElementById(elementID).value;
    }
    else {
        return null;
    }
}

var Panel = React.createClass({
  render: function() {
    var panelWidth = "col-md-"+this.props.panelWidth;
    var panelOffset = "col-md-offset-"+this.props.panelOffset;
    var colClasses = 'col ' + panelWidth + ' ' + panelOffset;
    var panelC = "panel";
    var panelColor = "panel-"+ this.props.panelColor;
    var panelClasses = 'panel ' + panelC + ' ' + panelColor;
    return (
      <div className="row">
        <div className={colClasses}>
          <div className={panelClasses}>
              <PanelHeader panelHeadingClasses={this.props.panelHeadingClasses}
                           panelHeadingContent={this.props.panelHeadingContent} />
              <PanelBody panelBodyClasses={this.props.panelBodyClasses}
                         tableClasses={this.props.tableClasses}
                         contentType={this.props.contentType}
                         showStats={this.props.showStats}
                         suggestionListUrl={this.props.suggestionListUrl}
                         imageBaseUrl={this.props.imageBaseUrl}
                         medalListUrl={this.props.medalListUrl}
                         userProfileID={this.props.userProfileID}
                         requestUserID={this.props.requestUserID}
                         userStatsUrl={this.props.userStatsUrl} />
          </div>
        </div>
      </div>
    );
  }
});

var PanelHeader = React.createClass({
  render: function() {
    var ppanelHeadingClasses = this.props.panelHeadingClasses;
    var panelHeading = "panel-heading";
    var panelHeaderClasses = 'panel-header ' + panelHeading + ' ' + ppanelHeadingClasses;
    return (
      <div className={panelHeaderClasses}>{this.props.panelHeadingContent}</div>
    );
  }
});

var PanelBody = React.createClass({
  render: function() {
    var ppanelBodyClasses = this.props.panelBodyClasses;
    var panelBody = "panel-body";
    var panelBodyClasses = 'panel-body ' + panelBody + ' ' + ppanelBodyClasses;
    // Decide what content to show in the panel body
    var bodyContent;
    if (this.props.contentType == "user-stats-table") {
        bodyContent = <Table tableClasses={this.props.tableClasses}
                             contentType={this.props.contentType}
                             userStatsUrl={this.props.userStatsUrl}
                             suggestionListUrl={this.props.suggestionListUrl}
                             imageBaseUrl={this.props.imageBaseUrl}
                             userProfileID={this.props.userProfileID}
                             requestUserID={this.props.requestUserID}
                             medalListUrl={this.props.medalListUrl} />;
    } else if (this.props.contentType == "user-show-stats") {
        bodyContent = <UserShowStatsPanelBody showStats={this.props.showStats}
                                              suggestionListUrl={this.props.suggestionListUrl}
                                              userProfileID={this.props.userProfileID}
                                              requestUserID={this.props.requestUserID}
                                              imageBaseUrl={this.props.imageBaseUrl} />;
    }
    return (
      <div className={panelBodyClasses}>
        {bodyContent}
      </div>
    );
  }
});

var Table = React.createClass({
  render: function() {
    var ptableClasses = this.props.tableClasses;
    var table = "table";
    var tableClasses = 'table ' + table + ' ' + ptableClasses;
    // Decide what table to show
    var tableContents = [];
    if (this.props.contentType == "user-stats-table") {
        tableContents.push(<UserStatsTableBody key="1"
                                               userStatsUrl={this.props.userStatsUrl}
                                               userProfileID={this.props.userProfileID}
                                               requestUserID={this.props.requestUserID}
                                               imageBaseUrl={this.props.imageBaseUrl}
                                               medalListUrl={this.props.medalListUrl} />);
    } else if (this.props.contentType == "user-show-stats-table") {
        tableContents.push(<UserShowStatsTableBody key="1"
                                                   userID={this.props.userID}
                                                   showID={this.props.showID}
                                                   suggestionListUrl={this.props.suggestionListUrl}
                                                   imageBaseUrl={this.props.imageBaseUrl}
                                                   userProfileID={this.props.userProfileID} />);
    }
    return (
      <table className={tableClasses}>
        {tableContents}
      </table>
    );
  }
});

var Medal = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    // Get the medal data for the given key
    var medalUrl = this.props.medalListUrl + this.props.medalID + "/";
    $.ajax({
      url: medalUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    // Create the medal URL
    var medalURL = "/medals/#" + this.state.data.name;
    // Create the medal classes
    var medalClass = this.state.data.name + "-medal";
    var medalClasses = 'medal ' + medalClass + ' pull-left';
    return (
      <a href={medalURL}><div className={medalClasses}></div></a>
    );
  }
});

var BigButton = React.createClass({
  render: function() {
    var showID = this.props.showID;
    var buttonText = this.props.buttonText;
    var buttonColor = this.props.buttonColor;
    var buttonClass = "btn btn-" + buttonColor + " btn-block btn-lg text-center xx-large-font";
    var buttonLink = "#";
    if (this.props.buttonLink) {
        buttonLink = this.props.buttonLink;
    } else if (showID) {
        buttonLink = this.props.channelRecapsUrl + showID + "/";
    }
    return (
        <a className={buttonClass} href={buttonLink} role="button">
            {buttonText}
        </a>
    );
  }
});

var BigButtonDropdown = React.createClass({
  render: function() {
    var buttonType = this.props.buttonType;
    var buttonColor = this.props.buttonColor;
    var buttonClass = "btn btn-" + buttonColor + " btn-block btn-lg dropdown-toggle xx-large-font";
    var showsList = [];
    var showClass = "disabled";
    var showLink = this.props.showLeaderboardUrl;
    showsList.push(<li className={showClass}><a href={showLink}>Show</a></li>);
    return (
        <div className="btn-group" style="width: 100%">
          <button className={buttonClass} data-toggle="dropdown" aria-expanded="false">
            Sup&nbsp;<span className="caret "></span>
          </button>
          <ul className="dropdown-menu text-center x-large-font" role="menu" style="width: 100%">
                <li><a href="/leaderboards/">All-time Leaderboard</a></li>
                <li><a href="/leaderboards/start_date-mdY/end_date-mdY/">Span</a></li>
                {showsList}
          </ul>
        </div>
    );
  }
});

var MedalRows = React.createClass({
  render: function() {
    var arrayLength = this.props.medals.length;
    var rowList = [];
    var medalList = [];
    // Go through all the medal keys
    for (var i = 0; i < arrayLength; i++) {
        var medalID = this.props.medals[i];
        medalList.push(<Medal key={i}
                              medalID={medalID}
                              medalListUrl={this.props.medalListUrl} />);
        var currentNum = i+1;
        // Push the row and reset the current medal list every 5 medals
        if (currentNum % 5 == 0) {
            rowList.push(<div key={currentNum} className="row">{medalList}</div>);
            medalList = [];
        }
    }
    // If there are any remaining medals, form a remainder row
    if (medalList) {
        rowList.push(<div key="1" className="row">{medalList}</div>);
    }
    return (
        <div>{rowList}</div>
    );
  }
});

var UserStatsTableBody = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.userStatsUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    // Decide the stat column color
    var columnColor = "info";
    // Define classes
    var tdClasses = 'table-column ' + columnColor;
    if (!this.state.data){
        return (<tbody></tbody>);
    }
    // Create the user stats
    var statsList = [];
    var medalShare;
    if (this.props.userProfileID == this.props.requestUserID) {
        var imgSrc = this.props.imageBaseUrl + "facebook_share.png";
        medalShare = <img className="facebook-share" src={imgSrc} />;
    }
    statsList.push(<tr key="1"><td className={tdClasses}>Username: {this.state.data.username}</td></tr>);
    statsList.push(<tr key="2"><td className={tdClasses}>Suggestions: {this.state.data.suggestions}</td></tr>);
    statsList.push(<tr key="3"><td className={tdClasses}>Suggestion Wins: {this.state.data.wins}</td></tr>);
    statsList.push(<tr key="4"><td className={tdClasses}>Points: {this.state.data.points}</td></tr>);
    statsList.push(<tr key="5"><td>
                    Medals:<br/>
                    <MedalRows medals={this.state.data.medals}
                               medalListUrl={this.props.medalListUrl} />
                    {medalShare}
                 </td></tr>);

    return (
      <tbody>
        {statsList}
      </tbody>
    );
  }
});

var UserShowStats = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    // Get the leaderboard stats for the user
    var showStatsUrl = this.props.showListUrl + this.props.showStats.show + "/";
    $.ajax({
      url: showStatsUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    var showDate = new Date(this.state.data.created);
    var showDateFormatted = showDate.toDateString();
    return (
      <Panel panelWidth="6" panelOffset="3" panelColor="primary"
             panelHeadingContent={showDateFormatted} panelHeadingClasses="x-large-font"
             panelBodyClasses="large-font black-font"
             tableClasses="table-condensed black-font"
             contentType="user-show-stats"
             showStats={this.props.showStats}
             suggestionListUrl={this.props.suggestionListUrl}
             imageBaseUrl={this.props.imageBaseUrl}
             userProfileID={this.props.userProfileID}/>
    );
  }
});

var UserShowStatsPanelBody = React.createClass({
  render: function() {
    var statElements = [];
    // Create the user show stats (make sure the state is loaded first)
    if (this.props.showStats) {
        var showID = this.props.showStats.show;
        var showLink = "/" + this.props.showStats.channel_name + "/leaderboards/show/" + showID + "/";
        var recapLink = "/" + this.props.showStats.channel_name + "/recaps/show/" + showID + "/";
        var starImgSrc = this.props.imageBaseUrl + "star-sprite.png";
        statElements.push(<div key="1" className="row"><div className="col-md-12">Points Earned: {this.props.showStats.points}</div></div>);
        statElements.push(<div key="2" className="row"><div className="col-md-12">Winning Suggestions: {this.props.showStats.wins}</div></div>);
        statElements.push(<div key="3" className="row"><div className="col-md-12"><a href={showLink}>Show Leaderboard</a></div></div>);
        statElements.push(<div key="4" className="row"><div className="col-md-12"><a href={recapLink}>Show Recap</a></div></div>);
        statElements.push(<div key="5" className="row"><div className="col-md-12">Suggestions:</div></div>);
        statElements.push(<Table key="6"
                                 tableClasses="table-condensed black-font"
                                 contentType="user-show-stats-table"
                                 userStatsUrl={this.props.userStatsUrl}
                                 imageBaseUrl={this.props.imageBaseUrl}
                                 userProfileID={this.props.userProfileID}
                                 requestUserID={this.props.requestUserID}
                                 showID={showID}
                                 showStats={this.props.showStats}
                                 suggestionListUrl={this.props.suggestionListUrl} />);
        statElements.push(<div key="7" className="row"><div className="col-md-12"><img src={starImgSrc} /> = Winning Suggestion</div></div>);
        statElements.push(<div key="8" className="row"><div className="col-md-12"><span className="label label-info">&nbsp;&nbsp;</span> = Appeared in Voting</div></div>);
        statElements.push(<div key="9" className="row"><div className="col-md-12"><span className="label label-default light-gray-bg">&nbsp;&nbsp;</span> = Not Voted on</div></div>);
    }

    return (
        <div>{statElements}</div>
    );
  }
});

var UserShowStatsTableBody = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    // Get the suggestions for the user
    var userSuggestionsUrl = this.props.suggestionListUrl + "?user_id=" + this.props.userProfileID + "&show_id=" + this.props.showID;
    $.ajax({
      url: userSuggestionsUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    var showID = this.props.showID;
    var suggestionList = [];
    this.counter = 0;
    // Create the suggestion list
    this.state.data.map(function (suggestion) {
        this.counter++;
        var suggestionClass, starIMG, suggestionDisplay;
        // Used a different class if the suggestion won
        if (suggestion.used === true) {
            suggestionClass = "success";
            var imgSrc = this.props.imageBaseUrl + "star-sprite.png";
            starIMG =  <img src={imgSrc} />;
        } else if (suggestion.voted_on === true) {
            suggestionClass = "info";
        } else {
            suggestionClass = "active";
        }
        // If the suggestion was voted on during the show
        if (suggestion.voted_on === true) {
            suggestionDisplay = <a href={suggestionUrl}>{suggestion.value}{starIMG}</a>;
        } else {
            suggestionDisplay = suggestion.value;
        }
        var suggestionUrl = "/recap/" + showID + "/#" + suggestion.id;
        suggestionList.push(<tr key={this.counter}><td className={suggestionClass}>{suggestionDisplay}</td></tr>);
        return suggestionList;
    }, this);
    return (
        <tbody>{suggestionList}</tbody>
    );
  }
});

var ShowDisplay = React.createClass({
  getInitialState: function() {
    // Hide the nav bar
	$("#top-nav-bar").hide();
    return {data: []};
  },
  loadShowData: function() {
    var showDataUrl = this.props.showDataUrl;
    $.ajax({
      url: showDataUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  componentDidMount: function() {
    this.loadShowData();
    setInterval(this.loadShowData, this.props.pollInterval);
  },
  render: function() {
    var state;
    state = getURLParameterByName("state") || undefined;
    // Make sure the current state exists
    if (this.state.data && this.state.data.current_state !== undefined || state !== undefined){
        if (state == undefined) {
            state = this.state.data.current_state['state'];
        }
        var showStateDisplay;
        // Create the user stats
        if (state == "default") {
            showStateDisplay = <ShowDefaultDisplay showData={this.state.data} />;
        } else if (state == "all-players") {

        } else if (state == "player-pool") {

        } else if (state == "player-options") {
            showStateDisplay = <ShowPlayerOptionsDisplay showData={this.state.data} />;
        } else if (state == "options" || state == "test") {

        }
    }
    return (
        <div>
            <div className="row">
                <div className="col-sm-11">
                    <h3 className="text-center background-blue">
                        <a href="/" className="white-link">Host Domain</a>
                    </h3>
                </div>
            </div>
            {showStateDisplay}
        </div>
    );
  }
});

var ShowDefaultDisplay = React.createClass({
  render: function() {
    if (this.props.showData) {
        var leaderboardURL = "/leaderboards/show/" + this.props.showData.id + "/";
        // Create the intervals remaining buttons
        var remainingVoteTypes = [];
        this.props.showData.vote_types.map(function (voteType) {
            remainingVoteTypes.push(<RemainingIntervalsButton voteType={voteType} />);
            remainingVoteTypes.push(<br/>);
            return remainingVoteTypes;
        }, this);
        return (
            <div className="col-md-5 col-md-offset-3">
                <a className="text-center" href={leaderboardURL}>
                    <div className="btn btn-default btn-block btn-lg home-show-btn">Leaderboard</div>
                </a>
                <br/>
                <div className="row">
                    <div className="col-md-8 col-md-offset-2">
                        <img src="adventure-prov-logo-large.png" className="img-responsive img-thumbnail" />
                    </div>
                </div>
                {remainingVoteTypes}
            </div>
        );
    } else {
        return (<div></div>);
    }
  }
});

var ShowPlayerOptionsDisplay = React.createClass({
  render: function() {
    return (<div>Player-Options</div>);
  }
});

var RemainingIntervalsButton = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    // Get the vote type data
    var voteTypeUrl = "/api/v1/vote_type/" + this.props.voteType + "/";
    $.ajax({
      url: voteTypeUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    // Make sure the current state exists and is not a "test"
    if (this.state.data && this.state.data.name != "test") {
        var buttonStyle = {backgroundColor: this.state.data.button_color};
        return (
            <button className="btn btn-block btn-lg white-input x-large-font" style={buttonStyle}>{this.state.data.display_name} Remaining: {this.state.data.remaining_intervals}</button>
        );
    } else {
        return (<div></div>);
    }
  }
});

var UserStats = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    // Get the leaderboard stats for the user
    var leaderboardStatsUrl = this.props.leaderboardStatsUrl;
    $.ajax({
      url: leaderboardStatsUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    var showList;
    if (this.state.data){
        var showList = [];
        this.counter = 0;
        // Create the user stats
        this.state.data.map(function (showStats) {
          this.counter++;
          showList.push(<UserShowStats key={this.counter}
                                       showStats={showStats}
                                       showListUrl={this.props.showListUrl}
                                       suggestionListUrl={this.props.suggestionListUrl}
                                       imageBaseUrl={this.props.imageBaseUrl}
                                       userProfileID={this.props.userProfileID} />);
          return showList;
        }, this);
    }
    return (
      <div className="row">
      <br/>
      <Panel panelWidth="6" panelOffset="3" panelColor="danger"
             panelHeadingContent="User Account" panelHeadingClasses="x-large-font"
             panelBodyClasses="large-font black-font"
             tableClasses="table-condensed black-font"
             contentType="user-stats-table"
             suggestionListUrl={this.props.suggestionListUrl}
             imageBaseUrl={this.props.imageBaseUrl}
             medalListUrl={this.props.medalListUrl}
             userProfileID={this.props.userProfileID}
             requestUserID={this.props.requestUserID}
             userStatsUrl={this.props.userStatsUrl} />
      {showList}</div>
    );
  }
});

var Leaderboards = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    if (this.props.contentType == "channel-leaderboard") {
        // Get the leaderboard url for the whole channel
        var leaderboardUrl = this.props.channelLeaderboardUrl;
    }
    $.ajax({
      url: leaderboardUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    var recapButton = [];
    if (this.props.showID) {
        recapButton.push(<br />);
        recapButton.push(<BigButton buttonText="View Show Recap" buttonColor="danger" />);
    }
    return (
      <div className="row"><div className="col-md-6 col-md-offset-3">
          {recapButton}
      </div></div>
    );
  }
});

var RootComponent = React.createClass({
  render: function() {
    var rootType = getElementValueOrNull("rootType");
    var showListUrl = getElementValueOrNull("showListUrl");
    var suggestionListUrl = getElementValueOrNull("suggestionListUrl");
    var imageBaseUrl = getElementValueOrNull("imageBaseUrl");
    var medalListUrl = getElementValueOrNull("medalListUrl");
    var userProfileID = getElementValueOrNull("userProfileID");
    var requestUserID = getElementValueOrNull("requestUserID");
    var leaderboardStatsUrl = getElementValueOrNull("leaderboardStatsUrl");
    var userStatsUrl = getElementValueOrNull("userStatsUrl");
    var rootComponents = [];
    if (rootType == "user-account") {
        rootComponents.push(<UserStats key="1"
                                       showListUrl={showListUrl}
                                       suggestionListUrl={suggestionListUrl}
                                       imageBaseUrl={imageBaseUrl}
                                       medalListUrl={medalListUrl}
                                       userProfileID={userProfileID}
                                       requestUserID={requestUserID}
                                       leaderboardStatsUrl={leaderboardStatsUrl}
                                       userStatsUrl={userStatsUrl} />);
    }

    return (
      <div>{rootComponents}</div>
    );
  }
});

ReactDOM.render(
    <RootComponent />,
    document.getElementById('container-fluid')
);