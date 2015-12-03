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

function getSpanFormat(spanDate){
    var date = new Date(spanDate);
    var month = date.getMonth() + 1
    return month + "" + date.getDate() + date.getFullYear();
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
                         userAccountContext={this.props.userAccountContext} />
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
                             userAccountContext={this.props.userAccountContext} />;
    } else if (this.props.contentType == "user-show-stats") {
        bodyContent = <UserShowStatsPanelBody showStats={this.props.showStats}
                                              userAccountContext={this.props.userAccountContext} />;
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
                                               userAccountContext={this.props.userAccountContext} />);
    } else if (this.props.contentType == "user-show-stats-table") {
        tableContents.push(<UserShowStatsTableBody key="1"
                                                   showID={this.props.showID}
                                                   userAccountContext={this.props.userAccountContext} />);
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
    var medalUrl = this.props.userAccountContext.medalListAPIUrl + this.props.medalID + "/";
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
  componentDidUpdate: function() {

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

var Loading = React.createClass({
  render: function() {
    var barColor;
    if (!this.props.loadingBarColor) {
        var divStyle = {backgroundColor: "#333"};
    } else {
        var divStyle = {backgroundColor: this.props.loadingBarColor};
    }
    return (
        <div className="spinner">
            <div className="rect1" style={divStyle}></div>
            <div className="rect2" style={divStyle}></div>
            <div className="rect3" style={divStyle}></div>
            <div className="rect4" style={divStyle}></div>
            <div className="rect5" style={divStyle}></div>
        </div>
    );
  }
});

var BigButton = React.createClass({
  render: function() {
    var buttonClass = "btn btn-" + this.props.buttonColor + " btn-block btn-lg text-center x-large-font";
    return (
        <div className="row">
            <div className="col-md-6 col-md-offset-3">
                <a className={buttonClass} href={this.props.buttonLink} role="button">
                    {this.props.buttonText}
                </a>
            </div>
        </div>
    );
  }
});

var BigButtonDropdownContents = React.createClass({
  getInitialState: function() {
    return {shows: undefined,
            spans: undefined};
  },
  componentDidMount: function() {
    // Fetch the shows for the channel
    $.ajax({
      url: this.props.showAPIUrl,
      dataType: 'json',
      success: function(showData) {
        // If this is a channel leaderboard
        if (this.props.leaderboardContext) {
            // Fetch the leaderboard spans for the channel
            $.ajax({
              url: this.props.leaderboardContext.leaderboardSpanAPIUrl,
              dataType: 'json',
              success: function(spanData) {
                this.setState({shows: showData,
                               spans: spanData});
              }.bind(this),
              error: function(xhr, status, err) {
                console.error(this.props.url, status, err.toString());
              }.bind(this)
            });
        } else {
            this.setState({shows: showData});
        }
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  render: function() {
    var dropDownStyle = {width: "100%", textAlign: "center"};
    var dropDownList = [];
    this.counter = 1;

    if (this.props.leaderboardContext) {
        dropDownList.push(<li key={this.counter}><a href={this.props.baseLinkUrl}>All-time Leaderboard</a></li>);
    }

    if (this.state.spans) {
        // Create the leaderboard span list
        this.state.spans.map(function (span) {
            this.counter++;
            var startDate = getSpanFormat(span.start_date);
            var endDate = getSpanFormat(span.end_date);
            var spanUrl = this.props.baseLinkUrl + startDate + "/" + endDate + "/";
            dropDownList.push(<li key={this.counter}><a href={spanUrl}>{span.name}</a></li>);
        }, this);
    }

    if (this.state.shows) {
        // Create the show list
        this.state.shows.map(function (show) {
            var showClass = "";
            this.counter++;
            if (this.props.showID == show.id) {
                showClass = "disabled";
            }
            var showLink = this.props.baseLinkUrl + 'show/' + show.id + '/';
            var showDate = new Date(show.created);
            var showDateFormatted = showDate.toDateString();
            dropDownList.push(<li key={this.counter} className={showClass}><a href={showLink}>{showDateFormatted}</a></li>);
            return dropDownList;
        }, this);
    } else {
        dropDownList.push(<Loading key="999999"
                                   loadingBarColor="#fff" />);
    }
    return (
      <ul className="dropdown-menu x-large-font" role="menu" style={dropDownStyle}>
            {dropDownList}
      </ul>
    );
  }
});

var BigButtonDropdown = React.createClass({
  render: function() {
    var buttonGroupStyle = {width: "100%"};
    var buttonColor = this.props.buttonColor;
    var buttonClass = "btn btn-" + buttonColor + " btn-block btn-lg dropdown-toggle x-large-font";

    return (
        <div className="row">
            <div className="col-md-6 col-md-offset-3">
                <div className="btn-group" style={buttonGroupStyle}>
                  <button className={buttonClass} data-toggle="dropdown" aria-expanded="false">
                    {this.props.currentSelection}&nbsp;<span className="caret "></span>
                  </button>
                  <BigButtonDropdownContents leaderboardContext={this.props.leaderboardContext}
                                             showAPIUrl={this.props.leaderboardContext.showListAPIUrl}
                                             baseLinkUrl={this.props.baseLinkUrl}
                                             showID={this.props.showID} />
                </div>
            </div>
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
                              userAccountContext={this.props.userAccountContext} />);
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
      url: this.props.userAccountContext.userStatsAPIUrl,
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
    if (!this.state.data){
        return (<tbody><tr><td><Loading /></td></tr></tbody>);
    }
    // Decide the stat column color
    var columnColor = "info";
    // Define classes
    var tdClasses = 'table-column large-font ' + columnColor;
    var trClasses = 'spacing';
    // Create the user stats
    var statsList = [];
    var medalShare;
    if (this.props.userAccountContext.userProfileID == this.props.userAccountContext.requestUserID) {
        var imgSrc = this.props.userAccountContext.imageBaseUrl + "facebook_share.png";
        medalShare = <img className="facebook-share" src={imgSrc} />;
    }
    statsList.push(<tr key="1" className={trClasses}><td className={tdClasses}>Username: {this.state.data.username}</td></tr>);
    statsList.push(<tr key="2" className={trClasses}><td className={tdClasses}>Suggestions: {this.state.data.suggestions}</td></tr>);
    statsList.push(<tr key="3" className={trClasses}><td className={tdClasses}>Suggestion Wins: {this.state.data.wins}</td></tr>);
    statsList.push(<tr key="4" className={trClasses}><td className={tdClasses}>Points: {this.state.data.points}</td></tr>);
    statsList.push(<tr key="5" className={trClasses}><td>
                    Medals:<br/>
                    <MedalRows medals={this.state.data.medals}
                               userAccountContext={this.props.userAccountContext} />
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
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the leaderboard stats for the user
    var showStatsUrl = this.props.userAccountContext.showListUrl + this.props.showStats.show + "/";
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
    if (!this.state.data){
        return (<Loading />);
    }
    var showDate = new Date(this.state.data.created);
    var showDateFormatted = showDate.toDateString();
    return (
      <Panel panelWidth="6" panelOffset="3" panelColor="primary"
             panelHeadingContent={showDateFormatted} panelHeadingClasses="x-large-font"
             panelBodyClasses="large-font black-font"
             tableClasses="table-condensed black-font"
             contentType="user-show-stats"
             showStats={this.props.showStats}
             userAccountContext={this.props.userAccountContext} />
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
        var starImgSrc = this.props.userAccountContext.imageBaseUrl + "star-sprite.png";
        statElements.push(<div key="1" className="row"><div className="col-md-12">Points Earned: {this.props.showStats.points}</div></div>);
        statElements.push(<div key="2" className="row"><div className="col-md-12">Winning Suggestions: {this.props.showStats.wins}</div></div>);
        statElements.push(<div key="3" className="row"><div className="col-md-12"><a href={showLink}>Show Leaderboard</a></div></div>);
        statElements.push(<div key="4" className="row"><div className="col-md-12"><a href={recapLink}>Show Recap</a></div></div>);
        statElements.push(<div key="5" className="row"><div className="col-md-12">Suggestions:</div></div>);
        statElements.push(<Table key="6"
                                 tableClasses="table-condensed black-font"
                                 contentType="user-show-stats-table"
                                 userAccountContext={this.props.userAccountContext}
                                 showID={showID}
                                 showStats={this.props.showStats} />);
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
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the suggestions for the user
    var userSuggestionsUrl = this.props.userAccountContext.suggestionListAPIUrl + "?user_id=" + this.props.userAccountContext.userProfileID + "&show_id=" + this.props.showID;
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
    if (!this.state.data){
        return (<tbody><tr><td><Loading /></td></tr></tbody>);
    }
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
            var imgSrc = this.props.userAccountContext.imageBaseUrl + "star-sprite.png";
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
    var leaderboardStatsAPIUrl = this.props.userAccountContext.leaderboardStatsAPIUrl;
    $.ajax({
      url: leaderboardStatsAPIUrl,
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
                                       userAccountContext={this.props.userAccountContext}
                                       showStats={showStats} />);
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
             userAccountContext={this.props.userAccountContext} />
      {showList}</div>
    );
  }
});

var Leaderboard = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    var leaderboardUrl;
    if (this.props.leaderboardContext.contentType == "channel-leaderboard") {
        // Get the api leaderboard url for the whole channel
        leaderboardUrl = this.props.leaderboardContext.channelLeaderboardAPIUrl;
    } else if (this.props.leaderboardContext.contentType == "show-leaderboard") {
        // Get the api leaderboard url for the show
        leaderboardUrl = this.props.leaderboardContext.channelLeaderboardAPIUrl;
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
    var showID = this.props.leaderboardContext.showID;

    if (showID) {
        recapButton.push(<BigButtonDropdown key="1"
                                            buttonColor="primary"
                                            leaderboardContext={this.props.leaderboardContext}
                                            showAPIUrl={this.props.leaderboardContext.showListAPIUrl}
                                            baseLinkUrl={this.props.leaderboardContext.channelLeaderboardUrl}
                                            showID={this.props.leaderboardContext.showID}
                                            currentSelection={this.props.leaderboardContext.currentSelection} />);
        recapButton.push(<br key="2" />);
        recapButton.push(<BigButton key="3"
                                    buttonText="View Show Recap"
                                    buttonColor="danger"
                                    buttonLink={this.props.leaderboardContext.channelShowRecapUrl} />);
    }
    return (
      <div>{recapButton}</div>
    );
  }
});

var RootComponent = React.createClass({
  render: function() {
    var rootType = getElementValueOrNull("rootType");
    var rootComponents = [];
    if (rootType == "user-account") {
        var userAccountContext = {
            showListAPIUrl: getElementValueOrNull("showListAPIUrl"),
            suggestionListAPIUrl: getElementValueOrNull("suggestionListAPIUrl"),
            imageBaseUrl: getElementValueOrNull("imageBaseUrl"),
            medalListAPIUrl: getElementValueOrNull("medalListAPIUrl"),
            userProfileID: getElementValueOrNull("userProfileID"),
            requestUserID: getElementValueOrNull("requestUserID"),
            leaderboardStatsAPIUrl: getElementValueOrNull("leaderboardStatsAPIUrl"),
            userStatsAPIUrl: getElementValueOrNull("userStatsAPIUrl")
        };
        rootComponents.push(<UserStats key="1" userAccountContext={userAccountContext} />);
    } else if (rootType == "leaderboard") {
        var leaderboardContext = {
            channelID: getElementValueOrNull("channelID"),
            channelLeaderboardAPIUrl: getElementValueOrNull("channelLeaderboardAPIUrl"),
            channelShowRecapUrl: getElementValueOrNull("channelShowRecapUrl"),
            leaderboardSpanAPIUrl: getElementValueOrNull("leaderboardSpanAPIUrl"),
            medalListAPIUrl: getElementValueOrNull("medalListAPIUrl"),
            channelLeaderboardUrl: getElementValueOrNull("channelLeaderboardUrl"),
            contentType: getElementValueOrNull("contentType"),
            showID: getElementValueOrNull("showID"),
            currentSelection: getElementValueOrNull("currentSelection"),
            showListAPIUrl: getElementValueOrNull("showListAPIUrl")
        };
        rootComponents.push(<Leaderboard key="1" leaderboardContext={leaderboardContext} />);
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