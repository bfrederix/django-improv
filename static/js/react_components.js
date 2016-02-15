///////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////// UTILITY FUNCTIONS/////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

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

function showDateUTCToLocal(stringDate) {
    return moment(moment.utc(stringDate).toDate());
}

function showDateUTCToLocalFormat(stringDate) {
    return showDateUTCToLocal(stringDate).format("ddd. MMM. Do, YYYY @hA");
}

function getSpanFormat(spanDate){
    var date = new Date(spanDate);
    var month = date.getMonth() + 1
    return month + "" + date.getDate() + date.getFullYear();
}

function limitFileSize(event, elementID) {
    var input = document.getElementById(elementID);
      // Examine the input file
    if (input) {
        var file = input.files[0];
        // Make sure the file is less than 2 MB
        if (file && file.size > 2097152) {
            $('#'+elementID).parent('span').addClass('btn-danger');
            alert("Image file sizes must be smaller than 2MB");
            event.preventDefault();
        }
    }
}

function validateTextField(event, elementID, allowSpaces, customMessage) {
    var field = document.getElementById(elementID);
    var re;
    if (allowSpaces) {
        re = /^[\w- ]+$/;
    } else {
        re = /^[\w-]+$/;
    }
    if (!re.test(field.value) || field.value.length === 0) {
        $('#'+elementID).parent('div').addClass('has-error');
        if (customMessage) {
            alert(customMessage);
        } else {
            alert(elementID + ' must be a combination of letters, numbers, hyphens, or underscores');
        }
        event.preventDefault();
    }
}

function validateYoutubeField(event, elementID) {
    var field = document.getElementById(elementID);
    var re = /^.*((youtu.be\/)|(v\/)|(\/u\/\w\/)|(embed\/)|(watch\?))\??v?=?([^#\&\?]*).*/;
    if (field.value.length !== 0 && !re.test(field.value)) {
        $('#'+elementID).parent('div').addClass('has-error');
        alert(elementID + ' must be a valid Youtube link');
        event.preventDefault();
    }
}

function validateDropDown(event, elementID) {
    var field = document.getElementById(elementID);
    // Make sure a value has been selected
    if (field && field.value === "") {
        $('#'+elementID).parent('div').addClass('has-error');
        alert(elementID + ' is required.');
        event.preventDefault();
    }
}

function PageLink(i, char, current){
  var character = character || String(i);
  if (i !== current) {
      return (
        <li key={char}>
          <a href={"?page="+i}>{char}</a>
        </li>
      );
  } else {
      return (
        <li key={char} className="disabled"><a href="#">{char}</a></li>
      );
  }
}

function componentToHex(c) {
    var hex = c.toString(16);
    return hex.length == 1 ? "0" + hex : hex;
}

function rgbToHex(r, g, b) {
    return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
}

function hexToRgb(hex) {
    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

///////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////// BASE COMPONENTS /////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

var SetIntervalMixin = {
  componentWillMount: function() {
    this.intervals = [];
  },
  setInterval: function() {
    this.intervals.push(setInterval.apply(null, arguments));
  },
  componentWillUnmount: function() {
    this.intervals.forEach(clearInterval);
  }
};


var Slider = React.createClass({
  getDefaultProps: function() {
    return {
      redVal: "",
      greenVal: "",
      blueVal: ""
    }
  },
  updateVal: function() {
    this.props.onUserInput(
      this.refs.redVal.value,
      this.refs.greenVal.value,
      this.refs.blueVal.value
    )
  },
  render: function() {
    var redSliderInput, greenSliderInput, blueSliderInput;
    var hexValue = rgbToHex(parseInt(this.props.redVal),
                            parseInt(this.props.greenVal),
                            parseInt(this.props.blueVal));
    if (this.props.enabled === "True") {
        redSliderInput = <input className="col-xs-8" id="redSlider" ref="redVal" type="range" min="0" max="255" value={this.props.redVal} onChange={this.updateVal} />;
        greenSliderInput = <input className="col-xs-8" id="greenSlider" ref="greenVal" type="range" min="0" max="255" value={this.props.greenVal} onChange={this.updateVal} />;
        blueSliderInput = <input className="col-xs-8" id="blueSlider" ref="blueVal" type="range" min="0" max="255" value={this.props.blueVal} onChange={this.updateVal} />;
    } else {
        redSliderInput = <input className="col-xs-8" id="redSlider" disabled="true" ref="redVal" type="range" min="0" max="255" value={this.props.redVal} onChange={this.updateVal} />;
        greenSliderInput = <input className="col-xs-8" id="greenSlider" disabled="true" ref="greenVal" type="range" min="0" max="255" value={this.props.greenVal} onChange={this.updateVal} />;
        blueSliderInput = <input className="col-xs-8" id="blueSlider" disabled="true" ref="blueVal" type="range" min="0" max="255" value={this.props.blueVal} onChange={this.updateVal} />;
    }
    return (
      <div>
        <div className="form-group row">
          <label className="col-xs-4" htmlFor="redSlider">R - {this.props.redVal}</label>
          {redSliderInput}
        </div>
        <div className="form-group row">
          <label className="col-xs-4" htmlFor="greenSlider">G - {this.props.greenVal}</label>
          {greenSliderInput}
        </div>
        <div className="form-group row">
          <label className="col-xs-4" htmlFor="blueSlider">B - {this.props.blueVal}</label>
          {blueSliderInput}
        </div>
        <input type="hidden" name={this.props.inputName} value={hexValue}></input>
      </div>
    )
  }
});


var IntervalTimer = React.createClass({
  componentDidMount: function() {
      // Counter style examples: "MinuteCounter", "HourCounter"
      if (this.props.counterStyle) {
          var clock = $('#' + this.props.timerID).FlipClock(
              this.props.secondsRemaining, {
                  clockFace: this.props.counterStyle,
                  countdown: true
          });
      // Just a regular old countdown
      } else {
          var clock = $('#' + this.props.timerID).FlipClock(
              this.props.secondsRemaining, {
                  clockFace: 'Counter'
          });
          // For some reason we have to do this manually :P
          setTimeout(function() {
              setInterval(function() {
                  clock.decrement();
              }, 1000);
          });
      }

  },
  render: function() {
      return (
        <div id={this.props.timerID}></div>
      );
  }
});


var ColorBar = React.createClass({
  getDefaultProps: function() {
    return {
      redVal: "",
      greenVal: "",
      blueVal: ""
    }
  },
  render: function() {
    var redVal = this.props.redVal,
        greenVal = this.props.greenVal,
        blueVal = this.props.blueVal;

    var style = {
      backgroundColor:'rgb(' + redVal + ',' + greenVal + ',' + blueVal + ')'
    };
    return (
      <div className="color-bar" style={style}></div>
    )
  }
});

var ColorPicker = React.createClass({
  getInitialState: function() {
    // Convert hex to RGB, remove all whitespace from the hex
    var rgb = hexToRgb(this.props.hexColor.replace(/ /g,''));
    return {
      redValue: rgb.r,
      greenValue: rgb.g,
      blueValue: rgb.b
    }
  },
  handleUserInput: function(redValueFromDOM, greenValueFromDOM, blueValueFromDOM) {
    this.setState({
      redValue: redValueFromDOM,
      greenValue: greenValueFromDOM,
      blueValue: blueValueFromDOM
    });
  },
  render: function() {
    return (
      <div>
        <Slider
         redVal={this.state.redValue}
         greenVal={this.state.greenValue}
         blueVal={this.state.blueValue}
         onUserInput={this.handleUserInput}
         inputName={this.props.inputName}
         enabled={this.props.enabled}
         />
        <ColorBar
        redVal={this.state.redValue}
        greenVal={this.state.greenValue}
        blueVal={this.state.blueValue}
        />
      </div>
    )
  }
});

var StarImage = React.createClass({
  render: function() {
      return (
        <img src="/static/img/star-sprite.png" />
      );
  }
});

var CSRFProtect = React.createClass({
  render: function() {
      var divStyle = {display: "none"};
      return (
        <div style={divStyle}>
            <input type="hidden" name="csrfmiddlewaretoken" value={this.props.csrfToken} />
        </div>
      );
  }
});

var ModalConfirm = React.createClass({
  handleClick: function() {
      $('#'+this.props.formID).submit();
  },
  render: function() {
      var actionLink;
      if (this.props.action) {
        actionLink = <a id={this.props.submitID} onClick={this.handleClick} className="btn btn-danger btn-ok">{this.props.action}</a>;
      }
      return (
        <div className="modal fade" id={this.props.modalID} role="dialog">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h4 className="modal-title">{this.props.header}</h4>
                    </div>
                    <div className="modal-body">
                        <p>{this.props.message}</p>
                    </div>
                    <div className="modal-footer">
                        <button type="button" className="btn btn-default" data-dismiss="modal">{this.props.dismiss}</button>
                        {actionLink}
                    </div>
                </div>
            </div>
        </div>
        );
  }
});

var Pagination = React.createClass({
  render: function() {
      var pages = parseInt(this.props.maxPages) + 1;
      var current = parseInt(this.props.currentPage);
      var links = [];
      var pageList = [];

      // leading arrows
      if (current > 1) {
        links.push([1, "<<"]);
        links.push([current - 1, "<"]);
      }

      for (var i=current-3; i<current+4; i++) {
        if (i > 0 && i < pages) {
          links.push([i, i]);
        }
      }

      // tailing arrows
      if (current < pages) {
        links.push([current + 1, ">"]);
        links.push([pages - 1, ">>"]);
      }

      links.map(function(x){
          pageList.push(PageLink(x[0], x[1], current));
      }, current);

      return (
        <ul className="pagination large-font">
            {pageList}
        </ul>
    );
  }
});

var Label = React.createClass({
  render: function() {
    var labelClasses = "label label-" + this.props.labelColor;
    if (this.props.extraClasses) {
        labelClasses = labelClasses + " " + this.props.extraClasses;
    }
    return (
        <span className={labelClasses}>{this.props.labelContents}</span>
    );
  }
});

var Form = React.createClass({
  render: function() {
    var formID = "formfield";
    var formClass = "form-" + this.props.formStyle;
    if (this.props.formID) {
        formID = this.props.formID;
    }
    return (
      <form id={formID} className={formClass} role="form"
            action={this.props.formSubmitUrl} method="post"
            encType="multipart/form-data" onSubmit={this.props.onFormSubmit}>
        {this.props.formContents}
        <CSRFProtect csrfToken={this.props.csrfToken} />
      </form>
    );
  }
});

var FormGroup = React.createClass({
  render: function() {
    var labelClasses = "col-md-" + this.props.labelSize + " control-label";
    var inputSize = "col-md-" + this.props.inputSize;
    var helpBlock;
    var starImage = "";
    var docs;
    if (this.props.docs) {
        docs = <a target="_blank" href={this.props.docs}>Explained Here</a>;
    }
    if (this.props.helpBlock) {
        helpBlock = <span className="help-block">{this.props.helpBlock} {docs}</span>;
    }
    if (this.props.premium === "true") {
        starImage = <StarImage />;
    }
    return (
        <div className="form-group">
            <label className={labelClasses}>{starImage}{this.props.labelContents}</label>
            <div className={inputSize}>
                {this.props.input}
                {helpBlock}
            </div>
        </div>
    );
  }
});

var FormLabel = React.createClass({
  render: function() {
    var label;
    var labelContents;
    if (this.props.action) {
        labelContents = this.props.action;
        var labelColor = "primary";
    } else if (this.props.error) {
        labelContents = this.props.error;
        var labelColor = "danger";

    }
    return (
        <div className="row">
            <div className="col-md-6 col-md-offset-3">
                <Label labelColor={labelColor}
                       extraClasses="x-large-font"
                       labelContents={labelContents} />
                <br />
            </div>
         </div>
    );
  }
});

var Panel = React.createClass({
  render: function() {
    var panelWidth = "col-md-"+this.props.panelWidth;
    var panelOffset = "col-md-offset-"+this.props.panelOffset;
    var colClasses = 'col ' + panelWidth + ' ' + panelOffset;
    var panelClasses = 'panel panel-' + this.props.panelColor + ' highlight-shadow';
    var panelComponents = [];
    if (this.props.panelHeadingContent) {
        panelComponents.push(<PanelHeader key="1"
                                          panelHeadingClasses={this.props.panelHeadingClasses}
                                          panelHeadingStyle={this.props.panelHeadingStyle}
                                          panelHeadingContent={this.props.panelHeadingContent}
                                          panelHeadingLink={this.props.panelHeadingLink} />);
    }
    if (this.props.bodyContent) {
        panelComponents.push(<PanelBody key="2"
                                        panelBodyClasses={this.props.panelBodyClasses}
                                        bodyContent={this.props.bodyContent} />);
    }
    if (this.props.footerContent) {
        panelComponents.push(<PanelFooter key="3"
                                          panelFooterClasses={this.props.panelFooterClasses}
                                          footerContent={this.props.footerContent} />);
    }
    return (
      <div className="row">
        <div className={colClasses}>
          <div className={panelClasses}>
            {panelComponents}
          </div>
        </div>
      </div>
    );
  }
});

var PanelHeader = React.createClass({
  render: function() {
    var link;
    var panelHeaderClasses = 'panel-heading ' + this.props.panelHeadingClasses + " text-shadow";
    if (this.props.panelHeadingLink) {
        link = <span>(<a href={this.props.panelHeadingLink}>Read More</a>)</span>;
    }
    return (
      <div className={panelHeaderClasses} style={this.props.panelHeadingStyle}>{this.props.panelHeadingContent} {link}</div>
    );
  }
});

var PanelBody = React.createClass({
  render: function() {
    var panelBodyClasses = 'panel-body ' + this.props.panelBodyClasses;
    return (
      <div className={panelBodyClasses}>
        {this.props.bodyContent}
      </div>
    );
  }
});

var PanelFooter = React.createClass({
  render: function() {
    var panelFooterClasses = 'panel-footer ' + this.props.panelFooterClasses;
    return (
      <div className={panelFooterClasses}>
        {this.props.footerContent}
      </div>
    );
  }
});

var Medal = React.createClass({
  getInitialState: function() {
    return {data: []};
  },
  componentDidMount: function() {
    // Get the medal data for the given key
    var medalUrl = this.props.medalListAPIUrl + this.props.medalID + "/";
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
    var medalClasses = 'medal ' + medalClass + ' pull-left btn-shadow';
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

var PlayerImage = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the medal data for the given key
    var playerUrl = this.props.playerAPIUrl + this.props.playerID + "/";
    $.ajax({
      url: playerUrl,
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
    var playerName;
    if (!this.state.data){
        return (<Loading loadingBarColor="#fff" />);
    }
    if (this.props.showName) {
        playerName = <button className="btn btn-info btn-lg word-wrap xx-large-font btn-shadow text-shadow">{this.state.data.name}</button>
    }
    return (
        <div>
            <img src={this.state.data.photo_url} className="img-responsive img-thumbnail highlight-shadow" />
            <br />
            {playerName}
        </div>
    );
  }
});

var Image = React.createClass({
  render: function() {
    return (
      <img src={this.props.image_url} className="img-responsive img-thumbnail highlight-shadow" />
    );
  }
});

var BigButton = React.createClass({
  render: function() {
    var buttonClass = "btn btn-" + this.props.buttonColor + " btn-block btn-lg text-center x-large-font btn-shadow text-shadow";
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
        var allClass = "";
        if (!this.props.showID && !this.props.spanID) {
            var allClass = "disabled";
        }
        dropDownList.push(<li key={this.counter} className={allClass}><a href={this.props.baseLinkUrl}>All-time Leaderboard</a></li>);
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
            var showDateFormatted = showDateUTCToLocalFormat(show.created);
            dropDownList.push(<li key={this.counter} className={showClass}><a href={showLink}>{showDateFormatted}</a></li>);
            return dropDownList;
        }, this);
    } else {
        dropDownList.push(<Loading key="999999"
                                   loadingBarColor="#fff" />);
    }
    return (
      <ul className="dropdown-menu x-large-font text-shadow" role="menu" style={dropDownStyle}>
            {dropDownList}
      </ul>
    );
  }
});

var BigButtonDropdown = React.createClass({
  render: function() {
    var display;
    var buttonGroupStyle = {width: "100%"};
    var buttonColor = this.props.buttonColor;
    var buttonClass = "btn btn-" + buttonColor + " btn-block btn-lg dropdown-toggle x-large-font btn-shadow text-shadow";
    if (this.props.showID) {
        display = showDateUTCToLocalFormat(this.props.currentSelection);
    } else {
        display = this.props.currentSelection;
    }
    return (
        <div className="row">
            <div className="col-md-6 col-md-offset-3">
                <div className="btn-group" style={buttonGroupStyle}>
                  <button className={buttonClass} data-toggle="dropdown" aria-expanded="false">
                    {display}&nbsp;<span className="caret "></span>
                  </button>
                  <BigButtonDropdownContents leaderboardContext={this.props.leaderboardContext}
                                             showAPIUrl={this.props.showAPIUrl}
                                             baseLinkUrl={this.props.baseLinkUrl}
                                             showID={this.props.showID} />
                </div>
            </div>
        </div>
    );
  }
});

var DropDownSelect = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.listAPIUrl,
      dataType: 'json',
      success: function(data) {
        this.setState({data: data});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  componentDidUpdate: function(prev, next) {
      // Change the select into a multi-select if required
      if (this.props.multiple === "true") {
          $(ReactDOM.findDOMNode(this)).multiSelect();
      }
  },
  render: function() {
    var optionList = [];
    var selectID;
    var selectElement;
    var loadingBarColor;
    if (this.props.loadingBarColor) {
        loadingBarColor = this.props.loadingBarColor;
    } else {
        loadingBarColor = "#fff";
    }
    if (!this.state.data){
        return (<div>
                    <Loading loadingBarColor={loadingBarColor} />
                </div>);
    }
    if (!this.props.selectID) {
        selectID = "selectID";
    } else {
        selectID = this.props.selectID;
    }
    this.counter = 0;
    if (this.props.defaultText) {
        optionList.push(<option key="0" value="">{this.props.defaultText}</option>);
    }
    // Create the suggestion list
    this.state.data.map(function (item) {
        this.counter++;
        var display;
        if (this.props.convertCreatedTimestamp) {
            display = showDateUTCToLocalFormat(item.created);
        } else {
            display = item.name;
        }
        optionList.push(<option key={this.counter} value={item.id}>{display}</option>);
        return optionList;
    }, this);

    if (this.props.multiple === "true") {
        return (<select multiple="multiple" name={selectID} id={selectID} className="form-control">
                    {optionList}
                </select>);
    } else {
        return (<select id={selectID} className="form-control" name={selectID} onChange={this.props.selectEventHandler} defaultValue={this.props.defaultSelected}>
                    {optionList}
                </select>);
    }
  }
});


var BottomNavSelect = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.listAPIUrl,
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
    var optionList = [];
    var selectedID;
    var itemLink;
    if (!this.state.data){
        return (<div></div>);
    }
    this.counter = 0;
    // Create the suggestion list
    this.state.data.map(function (item) {
        this.counter++;
        itemLink = this.props.baseLinkUrl + item.id + "/";
        if (parseInt(this.props.selectedID) == item.id) {
            optionList.push(<li key={this.counter} className="active"><a href={itemLink}><span className="bottom-nav-item">{item.display_name}</span></a></li>);
        } else {
            optionList.push(<li key={this.counter}><a href={itemLink}><span className="bottom-nav-item">{item.display_name}</span></a></li>);
        }
        return optionList;
    }, this);

    return (
        <nav className="navbar navbar-inverse navbar-fixed-bottom nav-bottom" role="navigation">
            <div className="container-fluid">
                <div className="navbar-header text-shadow">
                    <li className="dropdown">
                        <a className="dropdown-toggle navbar-brand" data-toggle="dropdown" href="#"><span className="bottom-nav-item pull-left">{this.props.label}&nbsp;</span><div className="caret-up"></div></a>
                        <ul className="dropdown-menu" role="menu">
                            {optionList}
                        </ul>
                    </li>
                </div>
            </div>
        </nav>);
  }
});


///////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////// FORM COMPONENTS /////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

var ChannelCreateEditForm = React.createClass({
  getInitialState: function() {
    return {data: {name: "",
                   display_name: "",
                   short_description: "",
                   description: "",
                   website: "",
                   facebook_page: "",
                   buy_tickets_link: "",
                   next_show: "",
                   navbar_color: "#4596FF",
                   background_color: "#000000",
                   address: {street: "",
                             city: "",
                             state: "",
                             zipcode: ""}},
            key: "1"
    };
  },
  componentDidMount: function() {
    if (this.props.channelCreateEditContext.channelID) {
        $.ajax({
          url: this.props.channelCreateEditContext.channelAPIUrl,
          dataType: 'json',
          success: function(data) {
            this.setState({data: data,
                           key: "2"});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    }
  },
  onFormSubmit: function(event) {
      limitFileSize(event, 'teamPhotoFile');
      validateTextField(event, "name");
      validateTextField(event, "display_name", true);
  },
  render: function() {
    var actionText;
    if (this.props.channelCreateEditContext.channelID) { 
        actionText = "Edit Channel";
     } else {
        actionText = "Create Channel"; 
    }
    var formContents = [];
    // Premium features key
    formContents.push(<div key="premium-1" className="row"><div className="col-md-12"><StarImage /> = Premium Feature</div><br /><br /></div>);
    // Name Input
    var nameInput = <input type="text" id="name" name="name" defaultValue={this.state.data.name} className="form-control"></input>;
    formContents.push(<FormGroup key="1"
                                 labelSize="2"
                                 labelContents="Url Name*:"
                                 inputSize="5"
                                 input={nameInput}
                                 helpBlock="Required: Used as the url address and can only be letters, numbers, hyphens or underscores" />);
    // Display Name Input
    var displayNameInput = <input type="text" id="display_name" name="display_name" defaultValue={this.state.data.display_name} className="form-control"></input>;
    formContents.push(<FormGroup key="2"
                                 labelSize="2"
                                 labelContents="Display Name*:"
                                 inputSize="5"
                                 input={displayNameInput}
                                 helpBlock="Required: Used as the human readable name on the site" />);
    // Short Description Input
    var shortDescriptionInput = <textarea type="text" name="short_description" maxLength="100" rows="2" defaultValue={this.state.data.short_description} className="form-control"></textarea>;
    formContents.push(<FormGroup key="3"
                                 labelSize="2"
                                 labelContents="Short Description:"
                                 inputSize="7"
                                 input={shortDescriptionInput} />);
    // Description Input
    var DescriptionInput = <textarea type="text" name="description" rows="5" defaultValue={this.state.data.description} className="form-control"></textarea>;
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="Description:"
                                 inputSize="8"
                                 input={DescriptionInput}
                                 helpBlock="Used on the channel's about page" />);
    // Team Photo Input
    var teamPhotoInput = <div><span className="btn btn-primary btn-file"><input id="teamPhotoFile" type="file" name="teamPhotoFile"></input></span><Image image_url={this.state.data.team_photo_url} /></div>;
    formContents.push(<FormGroup key="6"
                                 labelSize="2"
                                 labelContents="Team Photo:"
                                 inputSize="3"
                                 input={teamPhotoInput}
                                 helpBlock="Used on the channel's about page and show display, must be smaller than 2MB" />);
    // Website Input
    var websiteInput = <input type="text" name="website" defaultValue={this.state.data.website} className="form-control"></input>;
    formContents.push(<FormGroup key="7"
                                 labelSize="2"
                                 labelContents="Website:"
                                 inputSize="7"
                                 input={websiteInput}
                                 helpBlock="Your group's external website" />);
    // Facebook Page Input
    var facebookPageInput = <input type="text" name="facebook_page" defaultValue={this.state.data.facebook_page} className="form-control"></input>;
    formContents.push(<FormGroup key="8"
                                 labelSize="2"
                                 labelContents="Facebook Page:"
                                 inputSize="7"
                                 premium="true"
                                 input={facebookPageInput}
                                 helpBlock="Your group's Facebook page, 'Like Our Page' links added for premium channels" />);
    // Buy Tickets Input
    var buyTicketsInput = <input type="text" name="buy_tickets_link" defaultValue={this.state.data.buy_tickets_link} className="form-control"></input>;
    formContents.push(<FormGroup key="9"
                                 labelSize="2"
                                 labelContents="Buy Tickets URL:"
                                 inputSize="7"
                                 premium="true"
                                 input={buyTicketsInput}
                                 helpBlock="The URL to buy tickets to your shows, premium feature only" />);
    // Next Show
    var nextShowInput = <input type="datetime-local" name="next_show" className="form-control" defaultValue={this.state.data.next_show.replace('Z','')}></input>;
    formContents.push(<FormGroup key="10"
                                 labelSize="2"
                                 labelContents="Next Show:"
                                 inputSize="5"
                                 input={nextShowInput}
                                 helpBlock="When your next show is scheduled, appears on your channel's homepage" />);
    // Navbar Color Input (Requires Premium)
    var navbarColorInput = <ColorPicker hexColor={this.state.data.navbar_color}
                                        inputName="navbar_color"
                                        enabled={this.props.channelCreateEditContext.isPremium} />;
    formContents.push(<FormGroup key="17"
                                 labelSize="2"
                                 labelContents="Navigation Bar Color:"
                                 inputSize="4"
                                 premium="true"
                                 input={navbarColorInput}
                                 helpBlock="The color of your channel's Navigation Bar" />);
    // Background Color Input (Requires Premium)
    var backgroundColorInput = <ColorPicker hexColor={this.state.data.background_color}
                                            inputName="background_color"
                                            enabled={this.props.channelCreateEditContext.isPremium} />;
    formContents.push(<FormGroup key="18"
                                 labelSize="2"
                                 labelContents="Background Color:"
                                 inputSize="4"
                                 premium="true"
                                 input={backgroundColorInput}
                                 helpBlock="The color of your channel's background" />);
    // ADDRESS //
    // Street Input
    var streetInput = <input type="text" name="street" defaultValue={this.state.data.address.street} className="form-control"></input>;
    formContents.push(<FormGroup key="12"
                                 labelSize="2"
                                 labelContents="Street Address:"
                                 inputSize="6"
                                 input={streetInput}
                                 helpBlock="The street address where you perform your shows, used for mapping" />);
    // City Input
    var cityInput = <input type="text" name="city" defaultValue={this.state.data.address.city} className="form-control"></input>;
    formContents.push(<FormGroup key="13"
                                 labelSize="2"
                                 labelContents="City:"
                                 inputSize="5"
                                 input={cityInput} />);
    // State Input
    var stateInput = <input type="text" name="state" maxLength="2" defaultValue={this.state.data.address.state} className="form-control"></input>;
    formContents.push(<FormGroup key="14"
                                 labelSize="2"
                                 labelContents="State:"
                                 inputSize="2"
                                 input={stateInput} />);
    // Zipcode Input
    var zipcodeInput = <input type="text" name="zipcode" defaultValue={this.state.data.address.zipcode} className="form-control"></input>;
    formContents.push(<FormGroup key="15"
                                 labelSize="2"
                                 labelContents="Zipcode:"
                                 inputSize="3"
                                 input={zipcodeInput} />);

    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow">{actionText}</button>;
    formContents.push(<FormGroup key="16"
                                 inputSize="2"
                                 input={submitButton} />);

    // The entire Form
    var bodyContent = <Form formStyle="horizontal"
                            formSubmitUrl={this.props.channelCreateEditContext.formSubmitUrl}
                            formContents={formContents}
                            onFormSubmit={this.onFormSubmit}
                            csrfToken={this.props.channelCreateEditContext.csrfToken} />
    return (
        <div key={this.state.key}>
            <br/>
            <br/>
            <FormLabel action={this.props.channelCreateEditContext.action}
                       error={this.props.channelCreateEditContext.error} />
            <Panel panelWidth="6" panelOffset="3" panelColor="info"
                   panelHeadingContent={actionText} panelHeadingClasses="x-large-font"
                   panelBodyClasses="white-background"
                   panelHeadingLink="http://docs.dumpedit.com/en/latest/channels.html"
                   bodyContent={bodyContent} />
        </div>
    );
  }
});

var PlayerForm = React.createClass({
  getInitialState: function() {
    return {data: {name: "",
                   active: true,
                   star: false},
            editPlayerID: undefined,
            key: "1"};
  },
  componentDidMount: function() {
    // If a show has been selected
    if (this.state.editPlayerID) {
        var playerAPIUrl = this.props.addPlayerContext.playerAPIUrl + this.state.editPlayerID + "/";
        $.ajax({
          url: playerAPIUrl,
          dataType: 'json',
          success: function(data) {
            this.setState({data: data,
                           editPlayerID: this.state.editPlayerID,
                           key: this.state.editPlayerID});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    }
  },
  onFormSubmit: function(event) {
      validateTextField(event, "player_name", true);
      limitFileSize(event, 'inputFile');
  },
  handleEditPlayer: function(event) {
      this.setState({editPlayerID: event.target.value}, function() {
          this.componentDidMount();
      });
  },
  render: function() {
    var formContents = [];
    // Player Name Input
    var playerNameInput = <input type="text" id="player_name" name="player_name" defaultValue={this.state.data.name} className="form-control"></input>;
    formContents.push(<FormGroup key="1"
                                 labelSize="2"
                                 labelContents="Player Name*:"
                                 inputSize="4"
                                 input={playerNameInput}/>);
    // Player Photo Input
    var playerPhotoInput = <div><br/><span className="btn btn-primary btn-file"><input id="inputFile" type="file" name="file"></input></span></div>;
    formContents.push(<FormGroup key="2"
                                 labelSize="2"
                                 labelContents="Upload Player Photo:"
                                 inputSize="4"
                                 input={playerPhotoInput}
                                 helpBlock="Image file size must be smaller than 2MB" />);
    // Active Input
    var activeInput = <input type="checkbox" name="active" value="1" defaultChecked={this.state.data.active}></input>;
    formContents.push(<FormGroup key="3"
                                 labelSize="2"
                                 labelContents="Player Active:"
                                 inputSize="4"
                                 input={activeInput}
                                 helpBlock="Check this if the player should appear in the Create Show form" />);
    // Star Input
    var starInput = <input type="checkbox" name="star" value="1" defaultChecked={this.state.data.star}></input>;
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="Featured Player:"
                                 inputSize="4"
                                 input={starInput}
                                 helpBlock="Check this if the player should be prioritized first in shows" />);
    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow">Create/Edit Player</button>;
    formContents.push(<FormGroup key="5"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Player Dropdown Input
    var playerEditInput = <DropDownSelect listAPIUrl={this.props.addPlayerContext.playerListAPIUrl}
                                          selectEventHandler={this.handleEditPlayer}
                                          selectID="playerID"
                                          defaultSelected={this.state.editPlayerID}
                                          defaultText="Select a Player to Edit"
                                          loadingBarColor="#000" />;
    formContents.push(<FormGroup key="6"
                                 labelSize="2"
                                 labelContents="Edit Player:"
                                 inputSize="4"
                                 input={playerEditInput}
                                 helpBlock="Select a player if you wish to edit them" />);
    if (this.state.editPlayerID) {
        formContents.push(<div key="7" className="row">
                            <div className="col-md-4 col-md-offset-2">
                                <PlayerImage playerAPIUrl={this.props.addPlayerContext.playerAPIUrl}
                                             playerID={this.state.editPlayerID}/>
                            </div>
                          </div>);
    }
    var bodyContent = <Form formStyle="horizontal"
                            formSubmitUrl={this.props.addPlayerContext.formSubmitUrl}
                            formContents={formContents}
                            onFormSubmit={this.onFormSubmit}
                            csrfToken={this.props.addPlayerContext.csrfToken} />
    return (
        <div key={this.state.key}>
            <FormLabel action={this.props.addPlayerContext.action}
                       error={this.props.addPlayerContext.error} />
            <Panel panelWidth="6" panelOffset="3" panelColor="info"
                   panelHeadingContent="Create/Edit Player" panelHeadingClasses="x-large-font"
                   panelBodyClasses="white-background"
                   panelHeadingLink="http://docs.dumpedit.com/en/latest/players.html"
                   bodyContent={bodyContent} />
        </div>
    );
  }
});


var SuggestionPoolForm = React.createClass({
  getInitialState: function() {
    return {data: {name: "",
                   display_name: "",
                   description: 'Instructive **Markdown** text used to help guide users on what suggestions to enter',
                   max_user_suggestions: 5,
                   admin_only: false,
                   require_login: false,
                   active: true},
            suggestionPoolID: undefined,
            key: "1"};
  },
  componentDidMount: function() {
    // If a show has been selected
    if (this.state.suggestionPoolID) {
        var suggestionPoolAPIUrl = this.props.suggestionPoolContext.suggestionPoolAPIUrl + this.state.suggestionPoolID + "/";
        $.ajax({
          url: suggestionPoolAPIUrl,
          dataType: 'json',
          success: function(data) {
            this.setState({data: data,
                           suggestionPoolID: this.state.suggestionPoolID,
                           key: this.state.suggestionPoolID});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    }
  },
  onFormSubmit: function(event) {
      validateTextField(event, "name");
      validateTextField(event, "display_name", true);
      validateTextField(event, "max_user_suggestions");
  },
  editEventHandler: function(event) {
      this.setState({suggestionPoolID: event.target.value}, function() {
          this.componentDidMount();
      });
  },
  render: function() {
    var formContents = [];
    // Premium features key
    formContents.push(<div key="premium-1" className="row"><div className="col-md-12"><StarImage /> = Premium Feature</div><br /><br /></div>);
    // Name Input
    var nameInput = <input type="text" id="name" name="name" defaultValue={this.state.data.name} className="form-control"></input>;
    formContents.push(<FormGroup key="1"
                                 labelSize="2"
                                 labelContents="Name*:"
                                 inputSize="4"
                                 input={nameInput}/>);
    // Display Name Input
    var displayNameInput = <input type="text" id="display_name" name="display_name" defaultValue={this.state.data.display_name} className="form-control"></input>;
    formContents.push(<FormGroup key="2"
                                 labelSize="2"
                                 labelContents="Display Name*:"
                                 inputSize="4"
                                 input={displayNameInput}
                                 helpBlock="Name that appears to users" />);
    // Description Input
    var descriptionInput = <textarea type="text" name="description" rows="5" defaultValue={this.state.data.description} className="form-control"></textarea>;
    formContents.push(<FormGroup key="3"
                                 labelSize="2"
                                 labelContents="Description:"
                                 inputSize="8"
                                 input={descriptionInput}
                                 helpBlock="Used to instruct users on what types of suggestions to enter. Supports Markdown."
                                 docs="http://docs.dumpedit.com/en/latest/suggestion_pools.html#suggestion-pools-description" />);
    // Max User Suggestions Input
    var maxUserSuggestionsInput = <input type="text" id="max_user_suggestions" name="max_user_suggestions" maxLength="3" defaultValue={this.state.data.max_user_suggestions} className="form-control"></input>;
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="User Suggestion Limit*:"
                                 inputSize="2"
                                 input={maxUserSuggestionsInput}
                                 helpBlock="How many suggestions each user can enter for this suggestion pool"
                                 docs="http://docs.dumpedit.com/en/latest/suggestion_pools.html#suggestion-pools-user-suggestion-limit" />);
    // Admin Only Input
    var adminOnlyInput = <input type="checkbox" name="admin_only" value="1" defaultChecked={this.state.data.admin_only}></input>;
    formContents.push(<FormGroup key="5"
                                 labelSize="2"
                                 labelContents="Admin Suggestions Only:"
                                 inputSize="4"
                                 input={adminOnlyInput}
                                 helpBlock="Check this if only admin can enter suggestions in this pool"
                                 docs="http://docs.dumpedit.com/en/latest/suggestion_pools.html#suggestion-pools-admin-suggestions-only" />);
    // Require Login Input (Requires Premium)
    if (this.props.suggestionPoolContext.isPremium === "True") {
        var requireLoginInput = <input type="checkbox" name="require_login" value="1" defaultChecked={this.state.data.require_login}></input>;
    } else {
        var requireLoginInput = <input type="checkbox" name="require_login" value="1" disabled="true"></input>;
    }
    formContents.push(<FormGroup key="6"
                                 labelSize="2"
                                 labelContents="Require Login:"
                                 premium="true"
                                 inputSize="5"
                                 input={requireLoginInput}
                                 helpBlock="Check this if users are required to login to add suggestions"
                                 docs="http://docs.dumpedit.com/en/latest/suggestion_pools.html#suggestion-pools-require-login" />);
    // Active Input
    var activeInput = <input type="checkbox" name="active" value="1" defaultChecked={this.state.data.active}></input>;
    formContents.push(<FormGroup key="7"
                                 labelSize="2"
                                 labelContents="Suggestion Pool Active:"
                                 inputSize="4"
                                 input={activeInput}
                                 helpBlock="Check this if the Suggestion Pool should appear in the Create/Edit Vote Types form" />);
    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow">Create/Edit Suggestion Pool</button>;
    formContents.push(<FormGroup key="8"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Suggestion Pool Dropdown Input
    var suggestionPoolEditInput = <DropDownSelect listAPIUrl={this.props.suggestionPoolContext.suggestionPoolListAPIUrl}
                                                  selectEventHandler={this.editEventHandler}
                                                  defaultSelected={this.state.suggestionPoolID}
                                                  defaultText="Select a Suggestion Pool to Edit"
                                                  loadingBarColor="#000" />;
    formContents.push(<FormGroup key="9"
                                 labelSize="2"
                                 labelContents="Edit Suggestion Pool:"
                                 inputSize="4"
                                 input={suggestionPoolEditInput}
                                 helpBlock="Select a Suggestion Pool if you wish to edit it" />);

    var bodyContent = <Form formStyle="horizontal"
                            formSubmitUrl={this.props.suggestionPoolContext.formSubmitUrl}
                            formContents={formContents}
                            onFormSubmit={this.onFormSubmit}
                            csrfToken={this.props.suggestionPoolContext.csrfToken} />
    return (
        <div key={this.state.key}>
            <FormLabel action={this.props.suggestionPoolContext.action}
                       error={this.props.suggestionPoolContext.error} />
            <Panel panelWidth="6" panelOffset="3" panelColor="info"
                   panelHeadingContent="Create/Edit Suggestion Pools" panelHeadingClasses="x-large-font"
                   panelBodyClasses="white-background"
                   panelHeadingLink="http://docs.dumpedit.com/en/latest/suggestion_pools.html"
                   bodyContent={bodyContent} />
        </div>
    );
  }
});

var VoteTypeForm = React.createClass({
  getInitialState: function() {
    return {data: {name: "",
                   display_name: "",
                   suggestion_pool: undefined,
                   preshow_selected: false,
                   intervals: "",
                   manual_interval_control: true,
                   style: undefined,
                   ordering: 0,
                   options: 3,
                   vote_length: 25,
                   result_length: 10,
                   button_color: "#1c33ff",
                   require_login: false,
                   active: true},
            voteTypeID: undefined,
            key: "1"};
  },
  componentDidMount: function() {
    // If a show has been selected
    if (this.state.voteTypeID) {
        var voteTypeAPIUrl = this.props.voteTypeContext.voteTypeAPIUrl + this.state.voteTypeID + "/";
        $.ajax({
          url: voteTypeAPIUrl,
          dataType: 'json',
          success: function(data) {
            this.setState({data: data,
                           voteTypeID: this.state.voteTypeID,
                           key: this.state.voteTypeID});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    }
  },
  onFormSubmit: function(event) {
      validateTextField(event, "name");
      validateTextField(event, "display_name", true);
      validateDropDown(event, "style");
      validateTextField(event, "ordering");
      validateTextField(event, "options");
      validateTextField(event, "vote_length");
      validateTextField(event, "result_length");
  },
  editEventHandler: function(event) {
      this.setState({voteTypeID: event.target.value}, function() {
          this.componentDidMount();
      });
  },
  render: function() {
    var formContents = [];
    // Premium features key
    formContents.push(<div key="premium-1" className="row"><div className="col-md-12"><StarImage /> = Premium Feature</div><br /><br /></div>);
    // Name Input
    var nameInput = <input type="text" id="name" name="name" defaultValue={this.state.data.name} className="form-control"></input>;
    formContents.push(<FormGroup key="1"
                                 labelSize="2"
                                 labelContents="Name*:"
                                 inputSize="4"
                                 input={nameInput}/>);
    // Display Name Input
    var displayNameInput = <input type="text" id="display_name" name="display_name" defaultValue={this.state.data.display_name} className="form-control"></input>;
    formContents.push(<FormGroup key="2"
                                 labelSize="2"
                                 labelContents="Display Name*:"
                                 inputSize="4"
                                 input={displayNameInput}
                                 helpBlock="Name that appears to users" />);
    // Style Dropdown Input
    var styleInput = <DropDownSelect listAPIUrl={this.props.voteTypeContext.voteStyleAPIUrl}
                                     defaultSelected={this.state.data.style}
                                     defaultText="Select a Voting Style"
                                     selectID="style" />;
    formContents.push(<FormGroup key="7"
                                 labelSize="2"
                                 labelContents="Voting Style*:"
                                 inputSize="6"
                                 input={styleInput}
                                 helpBlock='Select a voting style for the Vote Type.'
                                 docs="http://docs.dumpedit.com/en/latest/vote_types.html#vote-styles" />);
    // Suggestion Pool Dropdown Input
    var suggestionPoolInput = <DropDownSelect listAPIUrl={this.props.voteTypeContext.suggestionPoolListAPIUrl}
                                              defaultSelected={this.state.data.suggestion_pool}
                                              defaultText="Select a Suggestion Pool"
                                              selectID="suggestion_pool"
                                              loadingBarColor="#000" />;
    formContents.push(<FormGroup key="3"
                                 labelSize="2"
                                 labelContents="Suggestion Pool:"
                                 inputSize="6"
                                 input={suggestionPoolInput}
                                 helpBlock="Select a Suggestion Pool if the vote type requires suggestions (active suggestion pools only)"
                                 docs="http://docs.dumpedit.com/en/latest/suggestion_pools.html" />);
    // Intervals Input
    var intervalsInput = <input type="text" id="intervals" name="intervals" defaultValue={this.state.data.intervals} className="form-control"></input>;
    formContents.push(<FormGroup key="5"
                                 labelSize="2"
                                 labelContents="Intervals:"
                                 inputSize="7"
                                 input={intervalsInput}
                                 helpBlock="Used to specify minute intervals at which votes are introduced into the show. Must begin with 0. (ex. 0,3,6,8,9,10)"
                                 docs="http://docs.dumpedit.com/en/latest/vote_types.html#vote-types-interval" />);
    // Pre-show Selected Input
    var preshowSelectedInput = <input type="checkbox" name="preshow_selected" value="1" defaultChecked={this.state.data.preshow_selected}></input>;
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="Disallow Audience Voting:"
                                 inputSize="5"
                                 input={preshowSelectedInput}
                                 helpBlock="Check this if the winner should be automatically selected instead of allowing the audience to vote"
                                 docs="http://docs.dumpedit.com/en/latest/vote_types.html#vote-types-disallow-audience-voting" />);
    // Manual Interval Control Input
    var manualIntervalControlInput = <input type="checkbox" name="manual_interval_control" value="1" defaultChecked={this.state.data.manual_interval_control}></input>;
    formContents.push(<FormGroup key="6"
                                 labelSize="2"
                                 labelContents="Manual Interval Voting Control:"
                                 inputSize="5"
                                 input={manualIntervalControlInput}
                                 helpBlock='Check this if you want the "tech" to control when interval voting occurs' />);
    // ordering Input
    var orderingInput = <input type="text" id="ordering" name="ordering" maxLength="2" defaultValue={this.state.data.ordering} className="form-control"></input>;
    formContents.push(<FormGroup key="8"
                                 labelSize="2"
                                 labelContents="Order:"
                                 inputSize="5"
                                 input={orderingInput}
                                 helpBlock='The numeric order in which the voting types appear, either as buttons on the Show Control page, or otherwise.' />);
    // options Input
    var optionsInput = <input type="text" id="options" name="options" maxLength="1" defaultValue={this.state.data.options} className="form-control"></input>;
    formContents.push(<FormGroup key="9"
                                 labelSize="2"
                                 labelContents="Voting Options:"
                                 inputSize="5"
                                 input={optionsInput}
                                 helpBlock='The number of voting options that appear on the voting page. Make sure you choose a number that will fit on the Show Display screen. (Options ignored for player-only vote types)' />);
    // Vote Length Input
    var voteLengthInput = <input type="text" id="vote_length" name="vote_length" defaultValue={this.state.data.vote_length} className="form-control"></input>;
    formContents.push(<FormGroup key="10"
                                 labelSize="2"
                                 labelContents="Voting Length:"
                                 inputSize="3"
                                 input={voteLengthInput}
                                 helpBlock='How many seconds the voting period lasts' />);
    // result Length Input
    var resultLengthInput = <input type="text" id="result_length" name="result_length" defaultValue={this.state.data.result_length} className="form-control"></input>;
    formContents.push(<FormGroup key="11"
                                 labelSize="2"
                                 labelContents="Voted Result Display Length:"
                                 inputSize="4"
                                 input={resultLengthInput}
                                 helpBlock='How many seconds the results of the vote stays on the screen' />);
    // Button Color Input
    var buttonColorInput = <ColorPicker hexColor={this.state.data.button_color}
                                        inputName="button_color"
                                        enabled="True" />;
    formContents.push(<FormGroup key="12"
                                 labelSize="2"
                                 labelContents="Vote Type Color:"
                                 inputSize="4"
                                 input={buttonColorInput}
                                 helpBlock='The color designated to the Vote Type buttons and such' />);
    // Require Login Input (Premium or not)
    if (this.props.voteTypeContext.isPremium === "True") {
        var requireLoginInput = <input type="checkbox" name="require_login" value="1" defaultChecked={this.state.data.require_login}></input>;
    } else {
        var requireLoginInput = <input type="checkbox" name="require_login" value="1" disabled="true"></input>;
    }
    formContents.push(<FormGroup key="13"
                                 labelSize="2"
                                 labelContents="Require Login:"
                                 premium="true"
                                 inputSize="5"
                                 input={requireLoginInput}
                                 helpBlock="Check this if users are required to login to vote" />);
    // Active Input
    var activeInput = <input type="checkbox" name="active" value="1" defaultChecked={this.state.data.active}></input>;
    formContents.push(<FormGroup key="14"
                                 labelSize="2"
                                 labelContents="Vote Type Active:"
                                 inputSize="5"
                                 input={activeInput}
                                 helpBlock="Check this if the Vote Type should appear on the Create Show page" />);
    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow">Create/Edit Vote Type</button>;
    formContents.push(<FormGroup key="15"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Vote Type Dropdown Input
    var voteTypeEditInput = <DropDownSelect listAPIUrl={this.props.voteTypeContext.voteTypeListAPIUrl}
                                            selectEventHandler={this.editEventHandler}
                                            defaultSelected={this.state.voteTypeID}
                                            defaultText="Select a Vote Type to Edit"
                                            loadingBarColor="#000" />;
    formContents.push(<FormGroup key="16"
                                 labelSize="2"
                                 labelContents="Edit VoteType:"
                                 inputSize="4"
                                 input={voteTypeEditInput}
                                 helpBlock="Select a Vote Type if you wish to edit it" />);

    var bodyContent = <Form formStyle="horizontal"
                            formSubmitUrl={this.props.voteTypeContext.formSubmitUrl}
                            formContents={formContents}
                            onFormSubmit={this.onFormSubmit}
                            csrfToken={this.props.voteTypeContext.csrfToken} />
    return (
        <div key={this.state.key}>
            <FormLabel action={this.props.voteTypeContext.action}
                       error={this.props.voteTypeContext.error} />
            <Panel panelWidth="6" panelOffset="3" panelColor="info"
                   panelHeadingContent="Create/Edit Vote Types" panelHeadingClasses="x-large-font"
                   panelBodyClasses="white-background"
                   panelHeadingLink="http://docs.dumpedit.com/en/latest/vote_types.html"
                   bodyContent={bodyContent} />
        </div>
    );
  }
});


var ChannelShowForm = React.createClass({
  getInitialState: function() {
    return {data: {show_length: 180,
                   embedded_youtube: ""},
            showID: undefined,
            key: "1"};
  },
  componentDidMount: function() {
    // If a show has been selected
    if (this.state.showID) {
        var showAPIUrl = this.props.channelShowContext.showAPIUrl + this.state.showID + "/";
        $.ajax({
          url: showAPIUrl,
          dataType: 'json',
          success: function(data) {
            this.setState({data: data,
                           showID: this.state.showID,
                           key: this.state.showID});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    }
  },
  onFormSubmit: function(event) {
      limitFileSize(event, 'photoFile');
      validateTextField(event, "show_length", false, "Show length in minutes is required.");
      validateYoutubeField(event, "embedded_youtube");
  },
  editEventHandler: function(event) {
      this.setState({showID: event.target.value}, function() {
          this.componentDidMount();
      });
  },
  render: function() {
    var formContents = [];
    var bodyContent = [];
    // Premium features key
    formContents.push(<div key="premium-1" className="row"><div className="col-md-12"><StarImage /> = Premium Feature</div><br /><br /></div>);
    // Only change players and vote types during creation
    if (!this.state.showID) {
        // Vote Types Dropdown Input
        var voteTypesInput = <DropDownSelect listAPIUrl={this.props.channelShowContext.voteTypeListAPIUrl}
                                             selectID="vote_types"
                                             multiple="true"
                                             loadingBarColor="#000" />;
        formContents.push(<FormGroup key="1"
                                     labelSize="2"
                                     labelContents="Vote Types:"
                                     inputSize="6"
                                     input={voteTypesInput}
                                     helpBlock='Select Vote Types for the Show (active only)' />);
        // Players Dropdown Input
        var playersInput = <DropDownSelect listAPIUrl={this.props.channelShowContext.playerListAPIUrl}
                                           selectID="players"
                                           multiple="true"
                                           loadingBarColor="#000" />;
        formContents.push(<FormGroup key="2"
                                     labelSize="2"
                                     labelContents="Players:"
                                     inputSize="6"
                                     input={playersInput}
                                     helpBlock='Select Players for the Show (active only)' />);
    }

    // Show Length Input
    var showLengthInput = <input type="text" id="show_length" name="show_length" defaultValue={this.state.data.show_length} className="form-control"></input>;
    formContents.push(<FormGroup key="3"
                                 labelSize="2"
                                 labelContents="Show Display Length (minutes)*:"
                                 inputSize="6"
                                 input={showLengthInput}
                                 helpBlock="Length of the show display from creation until end in minutes (should be a large overestimate of minutes, not exact), required for knowing when the show display should end and channel functionality should return to normal."
                                 docs="http://docs.dumpedit.com/en/latest/shows.html#show-length" />);

    // Photo Link Input (Premium or Not)
    if (this.props.channelShowContext.isPremium === "True") {
        var photoLinkInput = <div><span className="btn btn-primary btn-file"><input id="photoFile" type="file" name="photoFile"></input></span><Image image_url={this.state.data.photo_link} /></div>;
    } else {
        var photoLinkInput = <div><span className="btn btn-primary btn-file"><input id="photoFile" type="file" name="photoFile" disabled="true"></input></span><Image image_url={this.state.data.photo_link} /></div>;
    }
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="Show Photo:"
                                 inputSize="6"
                                 premium="true"
                                 input={photoLinkInput}
                                 helpBlock="Photo from the show (can be added later), must be smaller than 2MB" />);

    // Youtube Input (Premium or Not)
    if (this.props.channelShowContext.isPremium === "True") {
        var youtubeInput = <input type="text" id="embedded_youtube" name="embedded_youtube" defaultValue={this.state.data.embedded_youtube} className="form-control"></input>;
    } else {
        var youtubeInput = <input type="text" id="embedded_youtube" name="embedded_youtube" disabled="true" defaultValue={this.state.data.embedded_youtube} className="form-control"></input>;
    }
    formContents.push(<FormGroup key="5"
                                 labelSize="2"
                                 labelContents="Youtube Url:"
                                 inputSize="6"
                                 premium="true"
                                 input={youtubeInput}
                                 helpBlock="Youtube video from the show (can be added later), must be a valid Youtube url" />);

    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow">Create/Edit Show</button>;
    formContents.push(<FormGroup key="6"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Show Dropdown Input
    var showEditInput = <DropDownSelect listAPIUrl={this.props.channelShowContext.showListAPIUrl}
                                        selectEventHandler={this.editEventHandler}
                                        defaultSelected={this.state.showID}
                                        defaultText="Select a Show to Edit"
                                        loadingBarColor="#000"
                                        convertCreatedTimestamp="True" />;
    formContents.push(<FormGroup key="7"
                                 labelSize="2"
                                 labelContents="Edit Show:"
                                 inputSize="4"
                                 input={showEditInput}
                                 helpBlock="Select a Show if you wish to edit it" />);

    bodyContent.push(<Form key="1"
                           formStyle="horizontal"
                           formSubmitUrl={this.props.channelShowContext.formSubmitUrl}
                           formContents={formContents}
                           onFormSubmit={this.onFormSubmit}
                           csrfToken={this.props.channelShowContext.csrfToken} />);
    // If a show id has been selected. Add a delete button
    if (this.state.showID) {
        var deleteContents = [];
        var message = "Are you sure you wish to delete the " + showDateUTCToLocalFormat(this.state.data.created) + " show?";
        // Delete Button
        deleteContents.push(<input key="1" type="button" value="DELETE SHOW" className="btn btn-info btn-shadow text-shadow" data-toggle="modal" data-target="#confirm-delete" />);
        deleteContents.push(<input key="2" type="hidden" name="delete" value={this.state.showID}></input>);
        deleteContents.push(<ModalConfirm key="3"
                                          modalID="confirm-delete"
                                          submitID="submit-delete"
                                          formID="deleteForm"
                                          action="Delete"
                                          dismiss="Cancel"
                                          header="Delete Show"
                                          message={message} />);
        bodyContent.push(<Form key="2"
                               formID="deleteForm"
                               formSubmitUrl={this.props.channelShowContext.formSubmitUrl}
                               formContents={deleteContents}
                               onFormSubmit={this.onFormSubmit}
                               csrfToken={this.props.channelShowContext.csrfToken} />);
    }
    return (
        <div key={this.state.key}>
            <FormLabel action={this.props.channelShowContext.action}
                       error={this.props.channelShowContext.error} />
            <Panel panelWidth="6" panelOffset="3" panelColor="info"
                   panelHeadingContent="Create/Edit/Delete Shows" panelHeadingClasses="x-large-font"
                   panelBodyClasses="white-background"
                   panelHeadingLink="http://docs.dumpedit.com/en/latest/shows.html"
                   bodyContent={bodyContent} />
        </div>
    );
  }
});


///////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////// LEADERBOARD COMPONENTS ////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

var MedalButtonForm = React.createClass({
  render: function() {
    // CHECK TO SEE IF MEDALS HAVE ALREADY BEEN AWARDED!!!!!!!!
    var medalActionLink = this.props.baseLinkUrl + 'show/' + this.props.showID + '/';
    var awardMedalInput = <div>
                            <input type="hidden" name="award_medals" value="True"></input>
                            <input type="submit" className="btn btn-warning btn-block btn-lg x-large-font btn-shadow text-shadow" value="Award Medals"></input>
                          </div>;
    var formContents = <FormGroup input={awardMedalInput} />
    return (
        <Form formStyle="inline"
              formSubmitUrl={medalActionLink}
              formContents={formContents} />
    );
  }
});


var ChannelLeaderboardTable = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.leaderboardContext.channelLeaderboardAPIUrl,
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
        return (<div className="table-responsive text-shadow">
                    <table className="table table-condensed large-font">
                        <thead>
                            <tr className="medium-background">
                                <th>Rank</th>
                                <th>Username</th>
                                <th>Suggestion Wins</th>
                                <th>Points</th>
                                <th>Show Wins</th>
                            </tr>
                        </thead>
                        <tbody><tr><td colSpan="5">
                            <Loading loadingBarColor="#fff"/>
                        </td></tr></tbody>
                    </table>
                </div>);
    }
    var tableList = [];
    this.counter = 0;
    this.startCount = this.props.leaderboardContext.maxPerPage * (this.props.leaderboardContext.page - 1);

    // Create the suggestion list
    this.state.data.map(function (leaderboardUser) {
        this.counter++;
        var rank = this.counter + this.startCount;
        var userUrl = this.props.leaderboardContext.usersUrl + leaderboardUser.user_id + "/?channel_name=" + this.props.leaderboardContext.channelName;
        tableList.push(<tr key={this.counter} className="light-background">
                            <td>{rank}</td>
                            <td><a href={userUrl}>{leaderboardUser.username}</a></td>
                            <td>{leaderboardUser.suggestion_wins}</td>
                            <td>{leaderboardUser.points}</td>
                            <td>{leaderboardUser.show_wins}</td>
                       </tr>);
        return tableList;
    }, this);
    return (
        <div className="table-responsive text-shadow">
            <table className="table table-condensed large-font">
                <thead>
                    <tr className="medium-background">
                        <th>Rank</th>
                        <th>Username</th>
                        <th>Suggestion Wins</th>
                        <th>Points</th>
                        <th>Show Wins</th>
                    </tr>
                </thead>
                <tbody>
                    {tableList}
                </tbody>
            </table>
            <Pagination maxPages={this.props.leaderboardContext.maxPages}
                        currentPage={this.props.leaderboardContext.page} />
        </div>
    );
  }
});


var ShowLeaderboardTable = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.leaderboardContext.leaderboardEntryAPIUrl,
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
        return (<div className="table-responsive text-shadow">
                    <table className="table table-condensed large-font">
                        <thead>
                            <tr className="medium-background">
                                <th>Rank</th>
                                <th>Username</th>
                                <th>Suggestion Wins</th>
                                <th>Points</th>
                                <th>Medals</th>
                            </tr>
                        </thead>
                        <tbody><tr><td colSpan="5">
                            <Loading loadingBarColor="#fff"/>
                        </td></tr></tbody>
                    </table>
                </div>);
    }
    var tableList = [];
    this.counter = 0;
    this.startCount = this.props.leaderboardContext.maxPerPage * (this.props.leaderboardContext.page - 1);

    // Create the suggestion list
    this.state.data.map(function (leaderboardUser) {
        this.counter++;
        var rank = this.counter + this.startCount;
        var userUrl = this.props.leaderboardContext.usersUrl + leaderboardUser.user_id + "/?channel_name=" + this.props.leaderboardContext.channelName;
        var medalList = [];
        // Go through all the medal keys
        for (var i = 0; i < leaderboardUser.medals.length; i++) {
            var medalID = leaderboardUser.medals[i];
            medalList.push(<Medal key={i}
                                  medalID={medalID}
                                  medalListAPIUrl={this.props.leaderboardContext.medalListAPIUrl} />);
        }
        tableList.push(<tr key={this.counter} className="light-background">
                            <td>{rank}</td>
                            <td><a href={userUrl}>{leaderboardUser.username}</a></td>
                            <td>{leaderboardUser.wins}</td>
                            <td>{leaderboardUser.points}</td>
                            <td>{medalList}</td>
                       </tr>);
        return tableList;
    }, this);
    return (
        <div className="table-responsive text-shadow">
            <br/>
            <table className="table table-condensed large-font">
                <thead>
                    <tr className="medium-background">
                        <th>Rank</th>
                        <th>Username</th>
                        <th>Suggestion Wins</th>
                        <th>Points</th>
                        <th>Medals</th>
                    </tr>
                </thead>
                <tbody>
                    {tableList}
                </tbody>
            </table>
        </div>
    );
  }
});

var Leaderboard = React.createClass({
  render: function() {
    var leaderboardComponents = [];
    var showID = this.props.leaderboardContext.showID;

    if (showID) {
        leaderboardComponents.push(<BigButtonDropdown key="1"
                                            buttonColor="primary"
                                            leaderboardContext={this.props.leaderboardContext}
                                            showAPIUrl={this.props.leaderboardContext.showListAPIUrl}
                                            baseLinkUrl={this.props.leaderboardContext.channelLeaderboardUrl}
                                            showID={this.props.leaderboardContext.showID}
                                            currentSelection={this.props.leaderboardContext.currentSelection} />);
        leaderboardComponents.push(<br key="2" />);
        leaderboardComponents.push(<BigButton key="3"
                                    buttonText="View Show Recap"
                                    buttonColor="danger"
                                    buttonLink={this.props.leaderboardContext.channelShowRecapUrl} />);
        // If this is a channel admin user and we haven't awarded medals
        if (this.props.leaderboardContext.isAdmin && !this.props.leaderboardContext.medalsAwarded) {
            leaderboardComponents.push(<MedalButtonForm key="4" baseLinkUrl={this.props.leaderboardContext.channelLeaderboardUrl}
                                                        showID={this.props.leaderboardContext.showID}/>);
        }
        leaderboardComponents.push(<div key="5" className="row"><div className="col-md-10 col-md-offset-1">
                             <ShowLeaderboardTable leaderboardContext={this.props.leaderboardContext}
                                                      showID={this.props.leaderboardContext.showID} />
                         </div></div>);
    }
    else if (this.props.leaderboardContext.channelID) {
        leaderboardComponents.push(<BigButtonDropdown key="1"
                                            buttonColor="primary"
                                            leaderboardContext={this.props.leaderboardContext}
                                            showAPIUrl={this.props.leaderboardContext.showListAPIUrl}
                                            baseLinkUrl={this.props.leaderboardContext.channelLeaderboardUrl}
                                            currentSelection={this.props.leaderboardContext.currentSelection} />);
        leaderboardComponents.push(<div key="2" className="row"><div className="col-md-10 col-md-offset-1">
                                 <br/>
                                 <ChannelLeaderboardTable leaderboardContext={this.props.leaderboardContext} />
                             </div></div>);
    }

    return (
      <div>{leaderboardComponents}</div>
    );
  }
});

///////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////// USER ACCOUNT COMPONENTS ////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

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
                              medalListAPIUrl={this.props.userAccountContext.medalListAPIUrl} />);
        var currentNum = i+1;
        // Push the row and reset the current medal list every 5 medals
        if (currentNum % 5 == 0) {
            rowList.push(<span key={currentNum} className="row">{medalList}</span>);
            medalList = [];
        }
    }
    // If there are any remaining medals, form a remainder row
    if (medalList) {
        rowList.push(<span key="1" className="row">{medalList}</span>);
    }
    return (
        <span>{rowList}</span>
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
        return (<div className="table-responsive">
                    <table className="table table-condensed black-font">
                        <tbody><tr><td><Loading /></td></tr></tbody>
                    </table>
                </div>);
    }
    // Decide the stat column color
    var columnColor = "info";
    // Define classes
    var tdClasses = 'table-column large-font ' + columnColor;
    var trClasses = 'spacing';
    // Create the user stats
    var statsList = [];
    var medalShare;
    // Share medals on Facebook
    if (this.props.userAccountContext.userProfileID == this.props.userAccountContext.requestUserID) {
        // var imgSrc = this.props.userAccountContext.imageBaseUrl + "facebook_share.png";
        // medalShare = <img className="facebook-share" src={imgSrc} />;
    }
    statsList.push(<tr key="1" className={trClasses}><td className={tdClasses}>Username: {this.state.data.username}</td></tr>);
    statsList.push(<tr key="2" className={trClasses}><td className={tdClasses}>Suggestions: {this.state.data.suggestions}</td></tr>);
    statsList.push(<tr key="3" className={trClasses}><td className={tdClasses}>Suggestion Wins: {this.state.data.wins}</td></tr>);
    statsList.push(<tr key="4" className={trClasses}><td className={tdClasses}>Points: {this.state.data.points}</td></tr>);
    // If they have medals
    if (this.state.data.medals.length) {
        statsList.push(<tr key="5" className={trClasses}><td>
                    Medals:<br/>
                    <MedalRows medals={this.state.data.medals}
                               userAccountContext={this.props.userAccountContext} />
                    {medalShare}
                 </td></tr>);
    }

    return (
        <div className="table-responsive text-shadow">
            <table className="table table-condensed black-font">
                <tbody>
                    {statsList}
                </tbody>
            </table>
        </div>
    );
  }
});

var UserShowStats = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the leaderboard stats for the user
    var showStatsUrl = this.props.userAccountContext.showListAPIUrl + this.props.showStats.show + "/";
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
    var showDateFormatted = showDateUTCToLocalFormat(this.state.data.created);
    var bodyContent = <UserShowStatsPanelBody showStats={this.props.showStats}
                                              userAccountContext={this.props.userAccountContext} />;
    return (
      <Panel panelWidth="6" panelOffset="3" panelColor="primary"
             panelHeadingContent={showDateFormatted} panelHeadingClasses="x-large-font"
             panelBodyClasses="large-font black-font"
             tableClasses="table-condensed black-font"
             bodyContent={bodyContent} />
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
        statElements.push(<div key="1" className="row"><div className="col-md-12">Points Earned: {this.props.showStats.points}</div></div>);
        statElements.push(<div key="2" className="row"><div className="col-md-12">Winning Suggestions: {this.props.showStats.wins}</div></div>);
        statElements.push(<div key="3" className="row"><div className="col-md-12"><a href={showLink}>Show Leaderboard</a></div></div>);
        statElements.push(<div key="4" className="row"><div className="col-md-12"><a href={recapLink}>Show Recap</a></div></div>);
        statElements.push(<div key="5" className="row"><div className="col-md-12">Suggestions:</div></div>);
        statElements.push(<UserShowStatsTableBody key="6"
                                                  userAccountContext={this.props.userAccountContext}
                                                  showID={showID}
                                                  showStats={this.props.showStats} />);
        statElements.push(<div key="7" className="row"><div className="col-md-12"><StarImage /> = Winning Suggestion</div></div>);
        statElements.push(<div key="8" className="row"><div className="col-md-12"><Label labelColor="info" labelContents="&nbsp;&nbsp;" /> = Appeared in Voting</div></div>);
        statElements.push(<div key="9" className="row"><div className="col-md-12"><Label labelColor="info" extraClasses="light-gray-bg" labelContents="&nbsp;&nbsp;" /> = Not Voted on</div></div>);
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
        return (<div className="table-responsive">
                    <table className="table table-condensed black-font">
                        <tbody><tr><td><Loading /></td></tr></tbody>
                    </table>
                </div>);
    }
    var suggestionList = [];
    this.counter = 0;
    // Create the suggestion list
    this.state.data.map(function (suggestion) {
        this.counter++;
        var suggestionClass, starIMG, suggestionDisplay;
        // Used a different class if the suggestion won
        if (suggestion.used === true) {
            suggestionClass = "success";
        } else if (suggestion.voted_on === true) {
            suggestionClass = "info";
        } else {
            suggestionClass = "active";
        }
        // If the suggestion was used during the show
        if (suggestion.used === true) {
            suggestionDisplay = <td className={suggestionClass}><span className="text-shadow">{suggestion.value}</span><StarImage /></td>;
        } else {
            suggestionDisplay = <td className={suggestionClass}>{suggestion.value}</td>;
        }
        suggestionList.push(<tr key={this.counter}>{suggestionDisplay}</tr>);
        return suggestionList;
    }, this);
    return (
        <div className="table-responsive">
            <table className="table table-condensed black-font">
                <tbody>{suggestionList}</tbody>
            </table>
        </div>
    );
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
    var bodyContent = [];
    bodyContent.push(<UserStatsTableBody key="1"
                                         tableClasses="table-condensed black-font"
                                         userAccountContext={this.props.userAccountContext} />);
    return (
      <div className="row">
      <br/>
      <Panel panelWidth="6" panelOffset="3" panelColor="danger"
             panelHeadingContent="User Account" panelHeadingClasses="x-large-font"
             panelBodyClasses="large-font black-font"
             bodyContent={bodyContent} />
      {showList}</div>
    );
  }
});

//////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////// SHOW RECAP COMPONENTS /////////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////

var ShowMedia = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.showAPIUrl,
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
    var videoPanel;
    var photoPanel;
    if (!this.state.data){
        return (<div>
                    <Loading loadingBarColor="#fff"/>
                </div>);
    }

    if (this.state.data.photo_link) {
        var photoBodyContent = <div className="text-center"><Image image_url={this.state.data.photo_link} /></div>;
        photoPanel = <Panel key="1"
                            panelWidth="6" panelOffset="3" panelColor="warning"
                            panelHeadingContent="Recap Photo" panelHeadingClasses="x-large-font"
                            panelBodyClasses="large-font black-font"
                            bodyContent={photoBodyContent} />
    }

    if (this.state.data.embedded_youtube) {
        var videoBodyContent = <div className="embed-responsive embed-responsive-16by9">
                                   <iframe className="embed-responsive-item" src={this.state.data.embedded_youtube}></iframe>
                               </div>;
        videoPanel = <Panel key="2"
                            panelWidth="6" panelOffset="3" panelColor="warning"
                            panelHeadingContent="Recap Video" panelHeadingClasses="x-large-font"
                            panelBodyClasses="large-font black-font"
                            bodyContent={videoBodyContent} />
    }

    return (
        <div className="row">
            <div className="col-sm-12">
                {photoPanel}
                {videoPanel}
            </div>
        </div>
    );
  }
});

var ShowRecapPanelOptions = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    var recapOptionsUrl = this.props.recapContext.voteOptionAPIUrl + this.props.optionsID + "/";
    $.ajax({
      url: recapOptionsUrl,
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
        return (<div>
                    <Loading loadingBarColor="#fff"/>
                </div>);
    }

    var suggestionList = []
    for (var i = 0; i < this.state.data.length; i++) {
        var suggestion = this.state.data[i];
        var buttonClass = "btn-primary";
        var starImage = "";
        var user;
        if (this.props.winningSuggestion == suggestion.suggestion_id) {
            buttonClass = "btn-danger";
            starImage = <StarImage />;
        }
        if (suggestion.user_id) {
            var userUrl = this.props.recapContext.usersUrl + suggestion.user_id + "/?channel_name=" + this.props.recapContext.channelName;
            user = <a href={userUrl} className="recap-user-link">{suggestion.username}</a>;
        }
        else {
            user = "Anonymous";
        }
        var suggestionClass = "btn " + buttonClass + " btn-block large-font vote-option btn-shadow text-shadow";
        var suggestionCount = i + 1;
        suggestionList.push(<div key={i} id={suggestion.suggestion_id} className={suggestionClass}>
                                 {suggestionCount}. {suggestion.suggestion}{starImage}
                                 <br/>
                                 Submitted by: {user}
                            </div>)
    }

    return (
        <div key="1" className="row">
            <div className="col-sm-12">
                {suggestionList}
            </div>
        </div>
    );
  }
});

var ShowRecapPanels = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    $.ajax({
      url: this.props.recapContext.showRecapAPIUrl,
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
    var panelList = [];
    this.counter = 0;
    panelList.push(<br key="br-1" />);
    panelList.push(<ShowMedia key="sm-1" showAPIUrl={this.props.recapContext.showAPIUrl} />)
    if (this.state.data) {
        // Create the suggestion list
        this.state.data.map(function (recapItem) {
            this.counter++;
            var bodyContent;
            var footerContent;
            if (recapItem.player) {
                bodyContent = <div className="text-center recap-adjusted-img">
                                  <PlayerImage playerAPIUrl={this.props.recapContext.playerAPIUrl}
                                               playerID={recapItem.player}
                                               showName="True" />
                              </div>;
            }
            if (recapItem.options_id) {
                footerContent = <ShowRecapPanelOptions recapContext={this.props.recapContext}
                                                       winningSuggestion={recapItem.winning_suggestion}
                                                       optionsID={recapItem.options_id} />;
            }

            var brCounter = this.counter + 'br';
            panelList.push(<Panel key={this.counter}
                                  panelWidth="6" panelOffset="3" panelColor="info"
                                  panelHeadingContent={recapItem.vote_type} panelHeadingClasses="x-large-font"
                                  panelBodyClasses="large-font black-font"
                                  bodyContent={bodyContent}
                                  panelFooterClasses="black-background"
                                  footerContent={footerContent} />);
            return panelList;
        }, this);
    } else {
        panelList.push((<div key="load-1"><Loading loadingBarColor="#fff"/></div>));
    }

    return (
        <div>{panelList}</div>
    );
  }
});


var Recap = React.createClass({
  render: function() {
    var recapComponents = [];
    var showID = this.props.recapContext.showID;

    if (showID) {
        recapComponents.push(<BigButtonDropdown key="1"
                                                buttonColor="primary"
                                                showAPIUrl={this.props.recapContext.showListAPIUrl}
                                                baseLinkUrl={this.props.recapContext.channelRecapsUrl}
                                                showID={this.props.recapContext.showID}
                                                currentSelection={this.props.recapContext.currentSelection} />);
        recapComponents.push(<br key="2" />);
        recapComponents.push(<BigButton key="3"
                                        buttonText="View Show Leaderboard"
                                        buttonColor="danger"
                                        buttonLink={this.props.recapContext.channelShowLeaderboardUrl} />);
        // Recap panels
        recapComponents.push(<ShowRecapPanels key="4"
                                              recapContext={this.props.recapContext} />)
    }
    else {
        recapComponents.push(<BigButtonDropdown key="1"
                                                buttonColor="primary"
                                                showAPIUrl={this.props.recapContext.showListAPIUrl}
                                                baseLinkUrl={this.props.recapContext.channelRecapsUrl}
                                                currentSelection={this.props.recapContext.currentSelection} />);
    }

    return (
      <div>{recapComponents}</div>
    );
  }
});

//////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////// SHOW SUGGESTION POOL COMPONENTS ////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////

var ShowSuggestionPoolSuggestion = React.createClass({
  render: function() {
    var upvoteButton, deleteButton;
    var upvoteSpans = <div>
                          <span className="glyphicon glyphicon-circle-arrow-up"></span>
                          <span id={this.props.suggestion.id}>&nbsp;Upvote</span>
                      </div>;
    var votesID = this.props.suggestion.id + "-votes";
    var buttonID = this.props.suggestion.id + "-button";

    if (this.props.userID && this.props.suggestion.user_id == this.props.userID ||
        this.props.sessionID && this.props.suggestion.session_id == this.props.sessionID) {
        upvoteButton = <button className="btn btn-success text-shadow large-font" disabled="disabled" type="submit">
                           {upvoteSpans}
                       </button>;
        deleteButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow large-font">
                            <span className="glyphicon glyphicon-trash"></span>
                            <span>&nbsp;Delete</span>
                       </button>;
    } else if (this.props.suggestion.user_already_upvoted) {
        upvoteButton = <button className="btn btn-success text-shadow large-font" disabled="disabled" type="submit">
                           {upvoteSpans}
                       </button>;
    } else {
        upvoteButton = <button id={buttonID} onClick={this.props.handleUpvote} className="btn btn-success text-shadow large-font" type="submit">
                           {upvoteSpans}
                       </button>;
    }

    if (this.props.isChannelAdmin == "True") {
        deleteButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow large-font">
                            <span className="glyphicon glyphicon-trash"></span>
                            <span>&nbsp;Delete</span>
                       </button>;
    }

    return (
        <div>
            <div className="row">
                <div className="col-md-2 pull-left">
                    {upvoteButton}
                    &nbsp;&nbsp;<span id={votesID} className="black-font xx-large-font">{this.props.suggestion.preshow_value}</span>
                </div>
                <div className="col-md-8">
                    <span className="word-wrap black-font">{this.props.suggestion.value}</span>
                </div>
                <div className="col-md-2 pull-right">
                    <form action={this.props.deleteSubmitUrl} method="post">
                        <input type="hidden" name="delete_id" value={this.props.suggestion.id}/>
                        {deleteButton}
                        <CSRFProtect csrfToken={this.props.csrfToken} />
                    </form>
                </div>
            </div>
            <hr className="thick-divider bg-primary"/>
        </div>
    );
  }
});

var ShowSuggestionPoolAdd = React.createClass({
  render: function() {
    var maximum;
    var suggestalot;
    var displayName = this.props.showSuggestionPoolContext.suggestionPoolDisplayName;
    var suggestionInput = <input type="text" className="form-control" name="suggestion_value" />;
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow large-font">Add {displayName}</button>
    var description = markdown.toHTML(this.props.showSuggestionPoolContext.suggestionPoolDescription);
    if (this.props.showSuggestionPoolContext.suggestingDisabled) {
        maximum = <div className="bg-info large-font text-shadow">Maximum {displayName} suggestions entered. Please Upvote your favorites, or try another suggestion type.</div>;
        suggestionInput = <input type="text" className="form-control" name="suggestion_value" disabled />;
        submitButton = <button type="submit" className="btn btn-danger btn-shadow text-shadow large-font" disabled>Add {displayName}</button>;
    }
    if (this.props.showSuggestionPoolContext.suggestalot) {
        suggestalot = (
            <div className="row text-center">
                <br />
                <input type="hidden" id="suggestalot" name="suggestalot" value="true" readOnly></input>
                <button type="submit" className="btn btn-warning x-large-font">Suggest-a-lot</button>;
            </div>);
    }

    return (
        <div className="row">
            <div className="col-md-6 col-md-offset-3">
                <div className="panel panel-info highlight-shadow">
                    <div className="panel-heading large-font"><span className="underlay-object x-large-font text-shadow">Add {displayName}</span>
                        {maximum}
                        <div className="white-background well well-sm black-font" dangerouslySetInnerHTML={{__html: description}}></div>
                    </div>
                    <div className="panel-body">
                        <form action={this.props.showSuggestionPoolContext.formSubmitUrl} method="post">
                            <div className="row">
                                <div className="col-md-12">
                                    {suggestionInput}
                                </div>
                            </div>
                            <div className="row text-center">
                                {submitButton}
                            </div>
                            {suggestalot}
                            <CSRFProtect csrfToken={this.props.showSuggestionPoolContext.csrfToken} />
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
  }
});

var ShowSuggestionPool = React.createClass({
  mixins: [SetIntervalMixin], // Use the setInterval timing mixin
  getInitialState: function() {
    return {data: undefined,
            suggestionIDIndex: undefined};
  },
  componentDidMount: function() {
    // Initially Get the suggestions
    this.pullInitialSuggestions();
    // Set an interval to update the suggestions on
    this.setInterval(this.updateSuggestions, 5000);
  },
  pullInitialSuggestions: function() {
    $.ajax({
      url: this.props.showSuggestionPoolContext.suggestionListAPIUrl,
      dataType: 'json',
      success: function(data) {
        // Set the suggestion list index to the most recently pulled down suggestions
        var NewSuggestionIDIndex = data.map(
            function(suggestion) { return suggestion.id; }
        );
        this.setState({data: data,
                       suggestionIDIndex: NewSuggestionIDIndex});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  updateSuggestions: function() {
    $.ajax({
      url: this.props.showSuggestionPoolContext.suggestionListAPIUrl,
      dataType: 'json',
      success: function(data) {
        var orderedSuggestions;
        // If we have a previous suggestion list state
        if (this.state.data) {
            // Set the ordered suggestion to the old state
            orderedSuggestions = this.state.data;
            // Loop through the pulled down suggestion list
            data.map(function (suggestion) {
                // Get the index of the suggestions from the previous state's suggestion list
                var suggestionIndex = $.inArray(suggestion.id, this.state.suggestionIDIndex);
                // If the suggestion isn't in the old list
                if (suggestionIndex == -1) {
                    // Append it to the bottom of the list
                    orderedSuggestions.push(suggestion);
                // If the suggestion is in the list
                // AND it's still at the same index as it was before
                } else if (orderedSuggestions[suggestionIndex].id == suggestion.id) {
                    // Update the suggestion
                    orderedSuggestions[suggestionIndex] = suggestion;
                }
                return orderedSuggestions;
            }, this);

        } else {
            // Set the ordered suggestions for the first time
            orderedSuggestions = data;
        }
        // Set the suggestion list index to the most recently pulled down suggestions
        var NewSuggestionIDIndex = data.map(
            function(suggestion) { return suggestion.id; }
        );
        this.setState({data: orderedSuggestions,
                       suggestionIDIndex: NewSuggestionIDIndex});
      }.bind(this),
      error: function(xhr, status, err) {
        console.error(this.props.url, status, err.toString());
      }.bind(this)
    });
  },
  handleUpvote: function(event) {
      this.setState({data: this.state.data,
                     suggestionIDIndex: this.state.suggestionIDIndex}, function() {
          var suggestionID = event.target.id;
          var upvoteData = {id: suggestionID,
                            csrfmiddlewaretoken: this.props.showSuggestionPoolContext.csrfToken}
          // Do a POST to upvote the suggestion
          $.ajax({
              url: this.props.showSuggestionPoolContext.upvoteSubmitUrl,
              dataType: 'json',
              type: 'POST',
              data: upvoteData,
              success: function(data) {
                  // Update the votes
                  this.componentDidMount();
                  // Disable the upvote button for the suggestion
                  $(suggestionID+'-button').prop('disabled', true);
                  // Add one to the upvotes for that suggestion
                  var upvotes = $(suggestionID+'-votes');
                  upvotes.text(parseInt(upvotes.text())+1);
              }.bind(this),
              error: function(xhr, status, err) {
                  console.error(this.props.url, status, err.toString());
                  console.log(xhr.responseText);
              }.bind(this)
          });
      });
  },
  render: function() {
    var displayName = this.props.showSuggestionPoolContext.suggestionPoolDisplayName;
    var votePanelList = [];
    var addPanelList = [];
    var addHeading = "Add " + displayName;
    var voteHeading = "Vote for " + displayName;
    var baseSuggestionPoolUrl = this.props.showSuggestionPoolContext.channelHomeUrl + "show/" + this.props.showSuggestionPoolContext.showID + "/suggestion_pool/";
    this.counter = 0;
    if (this.state.data) {
        // Create the suggestion list
        this.state.data.map(function (suggestion) {
            this.counter++;
            votePanelList.push(<ShowSuggestionPoolSuggestion key={this.counter}
                                                             suggestion={suggestion}
                                                             userID={this.props.showSuggestionPoolContext.userID}
                                                             sessionID={this.props.showSuggestionPoolContext.sessionID}
                                                             isChannelAdmin={this.props.showSuggestionPoolContext.isChannelAdmin}
                                                             deleteSubmitUrl={this.props.showSuggestionPoolContext.formSubmitUrl}
                                                             csrfToken={this.props.showSuggestionPoolContext.csrfToken}
                                                             handleUpvote={this.handleUpvote} />);
            return votePanelList;
        }, this);
    } else {
        votePanelList.push((<div key="load-1"><Loading loadingBarColor="#000"/></div>));
    }

    return (
        <div className="row">
            <BottomNavSelect key="1"
                             selectedID={this.props.showSuggestionPoolContext.suggestionPoolID}
                             listAPIUrl={this.props.showSuggestionPoolContext.suggestionPoolListAPIUrl}
                             baseLinkUrl={baseSuggestionPoolUrl}
                             label="Suggestion Types" />
            <FormLabel key="2"
                       action={this.props.showSuggestionPoolContext.action}
                       error={this.props.showSuggestionPoolContext.error} />
            <ShowSuggestionPoolAdd key="3"
                                   showSuggestionPoolContext={this.props.showSuggestionPoolContext} />
            <Panel key="4"
                   panelWidth="6" panelOffset="3" panelColor="warning"
                   panelHeadingContent={voteHeading} panelHeadingClasses="x-large-font"
                   panelBodyClasses="large-font white-background"
                   bodyContent={votePanelList} />
            <br key="5" />
            <br key="6" />
        </div>
    );
  }
});


//////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////// SHOW CONTROLLER COMPONENTS ///////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////


var ShowControllerVoteType = React.createClass({
  mixins: [SetIntervalMixin], // Use the setInterval timing mixin
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Initially update the vote type
    this.updateVoteType()
    // Set an interval to update the vote types on (10 seconds)
    this.setInterval(this.updateVoteType, 10000);
  },
  updateVoteType: function() {
    var voteTypeAPIUrl = this.props.voteTypeAPIUrl + this.props.voteTypeID + "/?show_id=" + this.props.showID;
    $.ajax({
      url: voteTypeAPIUrl,
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
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }
    var buttonStyle = {backgroundColor: this.state.data.button_color};
    var voteTypeButton;
    var buttonText;
    var optionType = "";
    var availableOptions = this.state.data.available_options;
    var timerID = "timer-" + this.state.data.id;
    var intervalTimer;
    // Determine if the vote type is players or options
    if (!this.state.data.players_only) {
        optionType = "Suggestions";
    } else {
        optionType = "Players";
    }
    // Show what's available
    var availableText = optionType + ": " + this.state.data.available_options;
    // If the vote type has intervals
    if (this.state.data.intervals) {
        intervalTimer = <IntervalTimer key={this.state.data.interval_seconds_remaining}
                                       timerID={timerID}
                                       secondsRemaining={this.state.data.interval_seconds_remaining}
                                       counterStyle="MinuteCounter" />;
        // If there are still remaining intervals
        if (this.state.data.remaining_intervals) {
            // If the available options are greater than the remaining intervals
            if (this.state.data.available_options >= this.state.data.remaining_intervals ||
                this.state.data.players_only && !this.state.data.show_player_pool && !this.state.data.vote_type_player_pool) {
                buttonText = "Start the " + this.state.data.display_name + " Interval Vote (" + this.state.data.remaining_intervals + ")";
                voteTypeButton = (
                    <div>
                        <input key="1" type="hidden" name="vote_start" value={this.state.data.id} />
                        <input key="2" type="submit" className="btn btn-block btn-lg word-wrap white-input x-large-font btn-shadow text-shadow" style={buttonStyle} value={buttonText} />
                    </div>
                );
            // Not enough available options for the vote
            } else {
                // Make sure the button text isn't redundant
                if (this.state.data.vote_options_name !== optionType) {
                    buttonText = "Need more " + this.state.data.vote_options_name + " " + optionType + " (" + availableOptions + ")  ";
                } else {
                    buttonText = "Need more " + this.state.data.vote_options_name + " (" + availableOptions + ")  ";
                }
                voteTypeButton = <input disabled="true" type="submit" className="btn btn-block btn-lg word-wrap x-large-font btn-shadow text-shadow" style={buttonStyle} value={buttonText} />;
            }
        // No more intervals remain
        } else {
            buttonText = "No more " + this.state.data.display_name + " Intervals";
            voteTypeButton = <input disabled="true" type="submit" className="btn btn-block btn-lg word-wrap x-large-font btn-shadow text-shadow" style={buttonStyle} value={buttonText} />;
        }
    // If there are enough options for the vote
    } else if (this.state.data.available_options) {
        // If the vote type was already used
        if (this.state.data.vote_type_used) {
            buttonText = "No more " + this.state.data.display_name;
            voteTypeButton = <input disabled="true" type="submit" className="btn btn-block btn-lg word-wrap x-large-font btn-shadow text-shadow" style={buttonStyle} value={buttonText} />;
        } else {
            buttonText = "Start the " + this.state.data.display_name + " Vote";
            voteTypeButton = (
                <div>
                    <input key="1" type="hidden" name="vote_start" value={this.state.data.id} />
                    <input key="2" type="submit" className="btn btn-block btn-lg word-wrap white-input x-large-font btn-shadow text-shadow" style={buttonStyle} value={buttonText} />
                </div>
            );
        }
    // Not enough options for the vote
    } else {
        buttonText = "Need more " + this.state.data.vote_options_name + " " + optionType;
        voteTypeButton = <input disabled="true" type="submit" className="btn btn-block btn-lg word-wrap x-large-font btn-shadow text-shadow" style={buttonStyle} value={buttonText} />;
    }

    var voteTypePanelContents = (
        <div>
            <div className="row">
                <div className="col-md-6">
                    {voteTypeButton}
                </div>
                <div className="col-md-6">
                    {intervalTimer}
                </div>
            </div>
            <div className="row">
                <div className="col-md-12">
                    <br />
                    {availableText}
                </div>
            </div>
        </div>
    );

    var voteTypeForm = <Form formStyle="horizontal"
                             formSubmitUrl={this.props.formSubmitUrl}
                             formContents={voteTypePanelContents}
                             csrfToken={this.props.csrfToken} />;

    return (
        <Panel key="1"
               panelWidth="6" panelOffset="3" panelColor="danger"
               panelHeadingContent={this.state.data.display_name}
               panelHeadingStyle={buttonStyle}
               panelHeadingClasses="x-large-font"
               panelBodyClasses="large-font white-background"
               bodyContent={voteTypeForm} />
    );
  }
});


var ShowController = React.createClass({
  mixins: [SetIntervalMixin], // Use the setInterval timing mixin
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Initially update the show controller
    this.updateShowController()
    // Set an interval to update the show controller on (20 seconds)
    this.setInterval(this.updateShowController, 20000);
  },
  updateShowController: function() {
    if (this.props.showControllerContext.showAPIUrl) {
        $.ajax({
          url: this.props.showControllerContext.showAPIUrl,
          dataType: 'json',
          success: function(data) {
            this.setState({data: data});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    }
  },
  render: function() {
    if (!this.props.showControllerContext.showAPIUrl) {
        return (<div>Show has ended</div>);
    }
    var showLocked;
    var lockForm;
    var lockedText;
    var lockHelpText;
    var voteTypePanelList = [];
    var showRemaining;
    this.counter = 0;
    if (this.state.data) {
        if (this.state.data.locked) {
            lockedText = "Unlock";
            lockHelpText = "The audience currently cannot make new suggestions and are automatically redirected to the live voting page.";
        } else {
            lockedText = "Lock";
            lockHelpText = "The audience currently can make suggestions and use the site without being redirected to the voting page.";
        }
        // Create the Show Locked Content
        showLocked = (
            <div className="row">
                <div className="col-md-6">
                    <input key="1" type="hidden" name="lock_toggle" value="true" />
                    <input key="2" type="submit" className="btn btn-block btn-danger btn-lg word-wrap white-input x-large-font btn-shadow text-shadow" value={lockedText} />
                </div>
                <div className="col-md-6">
                    <p>{lockHelpText}</p>
                </div>
            </div>
        );
        lockForm = <Form formSubmitUrl={this.props.showControllerContext.formSubmitUrl}
                         formContents={showLocked}
                         csrfToken={this.props.showControllerContext.csrfToken} />
        // Create the vote type list
        this.state.data.vote_types.map(function (voteTypeID) {
            this.counter++;
            voteTypePanelList.push(<ShowControllerVoteType key={this.counter}
                                                           voteTypeID={voteTypeID}
                                                           showID={this.props.showControllerContext.showID}
                                                           voteTypeAPIUrl={this.props.showControllerContext.voteTypeAPIUrl}
                                                           formSubmitUrl={this.props.showControllerContext.formSubmitUrl}
                                                           csrfToken={this.props.showControllerContext.csrfToken} />);
            return voteTypePanelList;
        }, this);
        showRemaining = <IntervalTimer key={this.state.data.show_seconds_remaining}
                                       timerID="show-timer"
                                       secondsRemaining={this.state.data.show_seconds_remaining}
                                       counterStyle="HourCounter" />;
    } else {
        voteTypePanelList.push((<div key="load-1"><Loading loadingBarColor="#fff"/></div>));
    }

    return (
        <div>
            <Panel key="show-locked"
                   panelWidth="6" panelOffset="3" panelColor="danger"
                   panelHeadingContent="Suggesting Lock"
                   panelHeadingClasses="x-large-font"
                   panelBodyClasses="large-font white-background"
                   bodyContent={lockForm} />
            {voteTypePanelList}
            <Panel key="show-remaining"
                   panelWidth="6" panelOffset="3" panelColor="success"
                   panelHeadingContent="Show Remaining"
                   panelHeadingClasses="x-large-font"
                   panelBodyClasses="large-font white-background"
                   bodyContent={showRemaining} />
        </div>
    );
  }
});


//////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////// SHOW DISPLAY COMPONENTS ///////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////


var SuggestionOption = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the vote type data
    var voteTypeUrl = this.props.suggestionAPIUrl + this.props.suggestionID + "/";
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
    // If the vote type isn't loaded yet
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }
    return (
        <div>
            <button className="btn btn-block btn-primary btn-lg word-wrap x-large-font btn-shadow text-shadow">{this.props.optionNumber}. {this.state.data.value}</button>
        </div>
    );
  }
});

var RemainingIntervalsButton = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the vote type data
    var voteTypeUrl = this.props.voteTypeAPIUrl + this.props.voteTypeID + "/?show_id=" + this.props.showID;
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
    // If the vote type isn't loaded yet
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }
    // Make sure the current state has intervals
    if (this.state.data.intervals) {
        var buttonStyle = {backgroundColor: this.state.data.button_color};
        return (
            <div>
                <br/>
                <button className="btn btn-block btn-lg word-wrap white-input x-large-font btn-shadow text-shadow" style={buttonStyle}>{this.state.data.display_name} Remaining: {this.state.data.remaining_intervals}</button>
            </div>
        );
    } else {
        return (<div></div>);
    }
  }
});


var ShowDefaultDisplay = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the show leaderboard data
    $.ajax({
      url: this.props.showLeaderboardAPIUrl,
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
    // Create the intervals remaining buttons
    var remainingVoteTypes = [];
    var leaderboardEnties = [];
    var teamPhoto;
    var showLeaderboard;
    this.counter = 1;
    // Get the remaining vote types buttons
    this.props.showData.vote_types.map(function (voteTypeID) {
        remainingVoteTypes.push(
            <div key={voteTypeID} className="row">
                <div className="col-md-12">
                    <RemainingIntervalsButton voteTypeID={voteTypeID}
                                              showID={this.props.showID}
                                              voteTypeAPIUrl={this.props.voteTypeAPIUrl} />
                </div>
            </div>);
        return remainingVoteTypes;
    }, this);
    // Get the current top of the leaderboard
    if (this.state.data) {
        this.state.data.map(function (leaderboardEntry) {
            leaderboardEnties.push(<div className="btn btn-danger btn-block btn-shadow text-shadow large-font">{this.counter}. {leaderboardEntry.username}</div>);
            this.counter++;
            return leaderboardEnties;
        }, this);
    } else {
        leaderboardEnties.push(<Loading key="load" loadingBarColor="#fff" />);
    }
    if (this.props.teamPhotoUrl) {
        teamPhoto = (
            <div key="1" className="col-md-8">
                <Image image_url={this.props.teamPhotoUrl} />
            </div>);
        showLeaderboard = (
            <div key="2" className="col-md-4">
                <Panel panelWidth="12" panelColor="primary"
                   panelHeadingContent="Current Leaders" panelHeadingClasses="large-font"
                   bodyContent={leaderboardEnties} />
            </div>);
    } else if (this.state.data) {
        showLeaderboard = (
            <div key="2" className="col-md-12">
                <Panel panelWidth="12" panelColor="primary"
                   panelHeadingContent="Current Leaders" panelHeadingClasses="x-large-font"
                   bodyContent={leaderboardEnties} />
            </div>);
    }
    return (
        <div className="row">
            <div className="col-md-6 col-md-offset-3">
                <div key="leaderboard-0" className="row">
                    <div className="col-md-12">
                        <a className="text-center" href={this.props.showLeaderboardUrl}>
                            <div className="btn btn-info btn-block btn-lg btn-shadow text-shadow x-large-font">Leaderboard</div>
                        </a>
                        <br/>
                    </div>
                </div>
                <div key="team-leader-0" className="row">
                    {teamPhoto}{showLeaderboard}
                </div>
                {remainingVoteTypes}
            </div>
        </div>
    );
  }
});

var ShowResultDisplay = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the vote type data
    var voteTypeUrl = this.props.voteTypeAPIUrl + this.props.showData.current_vote_type + "/?show_id=" + this.props.showID;
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
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }
    var bodyContent;
    var submittedByText, submittedByButton;;
    var footerContent = [];
    var headingStyle = {backgroundColor: this.state.data.button_color};
    var voteTypeResult = this.state.data.display_name + " Result";
    // If there was a current voted player for this result
    if (this.state.data.current_voted_player) {
        bodyContent = (
            <div className="text-center">
                <PlayerImage playerAPIUrl={this.props.playerAPIUrl}
                             playerID={this.state.data.current_voted_player}
                             showName="True" />
            </div>
        );
    }
    // If there was a current voted suggestion for this result
    if (this.state.data.current_voted_suggestion) {
        footerContent.push(
            <SuggestionOption key="suggestion-option"
                              suggestionAPIUrl={this.props.suggestionAPIUrl}
                              suggestionID={this.state.data.current_voted_suggestion} />);
        // If it's not a players only vote
        if (!this.state.data.players_only) {
            // If a logged in user submitted the suggestion
            if (this.state.data.user) {
                submittedByText = "Submitted by: " + this.state.data.user;
            } else {
                submittedByText = "Submitted by: Anonymous";
            }
            submittedByButton = <button key="submitted-by" className="btn btn-primary btn-lg word-wrap xx-large-font btn-shadow text-shadow">{submittedByText}</button>;
        }
    }
    footerContent.push(
        <div key="submit-votes" className="row text-center">
            <button key="live-votes" className="btn btn-danger btn-lg word-wrap xx-large-font btn-shadow text-shadow">{this.state.data.live_votes} Votes</button>
            &nbsp;{submittedByButton}
        </div>
    );

    return (
        <div className="row">
            <div className="col-md-10 col-md-offset-1">
                <Panel panelWidth="12"
                       panelHeadingStyle={headingStyle}
                       panelHeadingContent={voteTypeResult} panelHeadingClasses="xx-large-font"
                       bodyContent={bodyContent}
                       footerContent={footerContent} />
            </div>
        </div>
    );
  }
});

var VoteOptionPlayer = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the vote option data
    var voteOptionUrl = this.props.voteOptionAPIUrl + this.props.voteOptionID + "/";
    $.ajax({
      url: voteOptionUrl,
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
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }
    var bodyContent = (
        <div className="text-center">
            <img src={this.state.data.player_photo} className="img-responsive img-thumbnail highlight-shadow" />
            <br />
            <button className="btn btn-info btn-md word-wrap x-large-font btn-shadow text-shadow">{this.state.data.player_name}</button>
        </div>
    );
    var footerContent = <button className="btn btn-primary btn-md btn-block word-wrap x-large-font btn-shadow text-shadow">{this.state.data.live_votes} Votes</button>;

    return (
        <Panel panelWidth="12" panelColor="primary"
               panelHeadingContent={this.state.data.option_number}
               panelHeadingStyle={this.props.headingStyle}
               panelHeadingClasses="xx-large-font text-center"
               bodyContent={bodyContent}
               footerContent={footerContent} />
    );
  }
});

var VoteOptionSuggestion = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the vote option data
    var voteOptionUrl = this.props.voteOptionAPIUrl + this.props.voteOptionID + "/";
    $.ajax({
      url: voteOptionUrl,
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
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }

    return (
        <button className="btn btn-primary btn-lg btn-block word-wrap xx-large-font btn-shadow text-shadow">
           {this.state.data.option_number}. {this.state.data.suggestion_value} {this.state.data.live_votes}
        </button>
    );
  }
});

var ShowVotingDisplay = React.createClass({
  getInitialState: function() {
    return {data: undefined};
  },
  componentDidMount: function() {
    // Get the vote type data
    var voteTypeUrl = this.props.voteTypeAPIUrl + this.props.showData.current_vote_type + "/?show_id=" + this.props.showID;
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
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }
    this.counter = 0;
    var votingDisplay = [];
    var footerContent = [];
    var headingStyle = {backgroundColor: this.state.data.button_color};
    var voteTypeHeading = this.state.data.display_name;
    // If this is a player only display
    if (this.state.data.players_only) {
        var intervalTimer = <IntervalTimer key={this.state.data.vote_seconds_remaining}
                                           timerID="countdown"
                                           secondsRemaining={this.state.data.vote_seconds_remaining} />;
        // Create the player list
        var playerOptionList = [];
        var rowKey, playerDivKey;
        var playersPerRow = 5;
        // Add the countdown to the first row
        playerOptionList.push(
            <div key={this.counter} className="col-md-2">
                <Panel key="countdown-panel"
                       panelWidth="12"
                       panelHeadingContent="Time Remaining"
                       panelHeadingStyle={headingStyle}
                       panelHeadingClasses="large-font"
                       bodyContent={intervalTimer} />
            </div>
        );
        this.props.showData.vote_options.map(function (voteOptionID) {
            this.counter++;
            rowKey = "row-" + this.counter;
            playerOptionList.push(
                <div key={this.counter} className="col-md-2">
                    <VoteOptionPlayer voteOptionID={voteOptionID}
                                      voteOptionAPIUrl={this.props.voteOptionAPIUrl}
                                      headingStyle={headingStyle} />
                </div>
            );
            // If we've either started our first row, or hit the next row
            if (this.counter % playersPerRow == 0) {
                // Create a row
                votingDisplay.push(
                    <div key={rowKey} className="row">
                        {playerOptionList}
                    </div>
                );
                //Reset the player option list
                playerOptionList = [];
            }
            return votingDisplay;
        }, this);
        // If there are any remaining items left in the player list
        if (playerOptionList) {
            // Create a row for the remainder
            votingDisplay.push(
                <div key="final-row" className="row">
                    {playerOptionList}
                </div>
            );
        }
    } else {
        var bodyContent;
        var footerContent = [];
        voteTypeHeading = voteTypeHeading + " Voting";
        // If we are viewing a vote with player options
        if (this.state.data.player_options) {
            // If we are viewing a vote with player options
            bodyContent = <PlayerImage playerAPIUrl={this.props.playerAPIUrl}
                                       playerID={this.state.data.current_voted_player}
                                       showName="True" />
        }
        this.props.showData.vote_options.map(function (voteOption) {
            this.counter++;
            footerContent.push(
                <div key={this.counter} className="row">
                    <div className="col-md-12">
                        <VoteOptionSuggestion voteOptionID={voteOption}
                                              voteOptionAPIUrl={this.props.voteOptionAPIUrl} />
                        <br />
                    </div>
                </div>
            );
            return footerContent;
        }, this);
        votingDisplay = <Panel panelWidth="12"
                               panelHeadingContent={voteTypeHeading}
                               panelHeadingStyle={headingStyle}
                               panelHeadingClasses="xx-large-font"
                               bodyContent={bodyContent}
                               footerContent={footerContent} />;
    }

    return (
        <div className="row">
            <div className="col-md-10 col-md-offset-1">
                {votingDisplay}
            </div>
        </div>
    );
  }
});


var ShowDisplay = React.createClass({
  mixins: [SetIntervalMixin], // Use the setInterval timing mixin
  getInitialState: function() {
    return {data: undefined};
  },
  loadShowData: function() {
    if (this.props.showDisplayContext.showAPIUrl) {
        $.ajax({
          url: this.props.showDisplayContext.showAPIUrl,
          dataType: 'json',
          success: function(data) {
            this.setState({data: data});
          }.bind(this),
          error: function(xhr, status, err) {
            console.error(this.props.url, status, err.toString());
          }.bind(this)
        });
    }
  },
  componentDidMount: function() {
    this.loadShowData();
    this.setInterval(this.loadShowData, 2000);
  },
  render: function() {
    // If the show has ended
    if (!this.props.showDisplayContext.showAPIUrl) {
        return (<div>Show has ended</div>);
    }
    // If the vote type isn't loaded yet
    if (!this.state.data) {
        return (<Loading loadingBarColor="#fff" />);
    }
    var showStateDisplay;
    // Default Show display
    if (this.state.data.current_display == "default") {
        showStateDisplay = <ShowDefaultDisplay showData={this.state.data}
                                               showID={this.props.showDisplayContext.showID}
                                               voteTypeAPIUrl={this.props.showDisplayContext.voteTypeAPIUrl}
                                               showLeaderboardAPIUrl={this.props.showDisplayContext.showLeaderboardAPIUrl}
                                               showLeaderboardUrl={this.props.showDisplayContext.channelShowLeaderboardUrl}
                                               teamPhotoUrl={this.props.showDisplayContext.teamPhotoUrl} />;
    } else if (this.state.data.current_display == "voting") {
        showStateDisplay = <ShowVotingDisplay showData={this.state.data}
                                              showID={this.props.showDisplayContext.showID}
                                              voteTypeAPIUrl={this.props.showDisplayContext.voteTypeAPIUrl}
                                              voteOptionAPIUrl={this.props.showDisplayContext.voteOptionAPIUrl} />;
    } else if (this.state.data.current_display == "result") {
        showStateDisplay = <ShowResultDisplay showData={this.state.data}
                                              showID={this.props.showDisplayContext.showID}
                                              playerAPIUrl={this.props.showDisplayContext.playerAPIUrl}
                                              voteTypeAPIUrl={this.props.showDisplayContext.voteTypeAPIUrl}
                                              liveVoteAPIUrl={this.props.showDisplayContext.liveVoteAPIUrl} />;
    }
    return (
        <div>
            {showStateDisplay}
        </div>
    );
  }
});

///////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////// ROOT COMPONENT ///////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

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
            channelName: getElementValueOrNull("channelName"),
            page: getElementValueOrNull("page"),
            maxPerPage: getElementValueOrNull("maxPerPage"),
            maxPages: getElementValueOrNull("maxPages"),
            channelLeaderboardAPIUrl: getElementValueOrNull("channelLeaderboardAPIUrl"),
            channelShowRecapUrl: getElementValueOrNull("channelShowRecapUrl"),
            leaderboardEntryAPIUrl: getElementValueOrNull("leaderboardEntryAPIUrl"),
            leaderboardSpanAPIUrl: getElementValueOrNull("leaderboardSpanAPIUrl"),
            medalListAPIUrl: getElementValueOrNull("medalListAPIUrl"),
            channelLeaderboardUrl: getElementValueOrNull("channelLeaderboardUrl"),
            usersUrl: getElementValueOrNull("usersUrl"),
            contentType: getElementValueOrNull("contentType"),
            showID: getElementValueOrNull("showID"),
            medalsAwarded: getElementValueOrNull("medalsAwarded"),
            currentSelection: getElementValueOrNull("currentSelection"),
            showListAPIUrl: getElementValueOrNull("showListAPIUrl"),
            isAdmin: getElementValueOrNull("isAdmin")
        };
        rootComponents.push(<Leaderboard key="1" leaderboardContext={leaderboardContext} />);
    } else if (rootType == "recap") {
        var recapContext = {
            channelName: getElementValueOrNull("channelName"),
            imageBaseUrl: getElementValueOrNull("imageBaseUrl"),
            showListAPIUrl: getElementValueOrNull("showListAPIUrl"),
            voteOptionAPIUrl: getElementValueOrNull("voteOptionAPIUrl"),
            playerAPIUrl: getElementValueOrNull("playerAPIUrl"),
            channelRecapsUrl: getElementValueOrNull("channelRecapsUrl"),
            currentSelection: getElementValueOrNull("currentSelection"),
            channelShowLeaderboardUrl: getElementValueOrNull("channelShowLeaderboardUrl"),
            showRecapAPIUrl: getElementValueOrNull("showRecapAPIUrl"),
            usersUrl: getElementValueOrNull("usersUrl"),
            showAPIUrl: getElementValueOrNull("showAPIUrl"),
            showID: getElementValueOrNull("showID")
        };
        rootComponents.push(<Recap key="1" recapContext={recapContext} />);
    } else if (rootType == "channel-create-edit") {
        var channelCreateEditContext = {
            channelID: getElementValueOrNull("channelID"),
            isPremium: getElementValueOrNull("isPremium"),
            channelAPIUrl: getElementValueOrNull("channelAPIUrl"),
            userID: getElementValueOrNull("userID"),
            formSubmitUrl: getElementValueOrNull("formSubmitUrl"),
            csrfToken: getElementValueOrNull("csrfToken"),
            action: getElementValueOrNull("action"),
            error: getElementValueOrNull("error")
        };
        rootComponents.push(<ChannelCreateEditForm key="1"
                                                   channelCreateEditContext={channelCreateEditContext} />);
    } else if (rootType == "channel_players") {
        var addPlayerContext = {
            playerAPIUrl: getElementValueOrNull("playerAPIUrl"),
            playerListAPIUrl: getElementValueOrNull("playerListAPIUrl"),
            formSubmitUrl: getElementValueOrNull("formSubmitUrl"),
            csrfToken: getElementValueOrNull("csrfToken"),
            action: getElementValueOrNull("action"),
            error: getElementValueOrNull("error")
        };
        rootComponents.push(<PlayerForm key="1" addPlayerContext={addPlayerContext} />);
    } else if (rootType == "channel_suggestion_pools") {
        var suggestionPoolContext = {
            isPremium: getElementValueOrNull("isPremium"),
            suggestionPoolAPIUrl: getElementValueOrNull("suggestionPoolAPIUrl"),
            suggestionPoolListAPIUrl: getElementValueOrNull("suggestionPoolListAPIUrl"),
            formSubmitUrl: getElementValueOrNull("formSubmitUrl"),
            csrfToken: getElementValueOrNull("csrfToken"),
            action: getElementValueOrNull("action"),
            error: getElementValueOrNull("error")
        };
        rootComponents.push(<SuggestionPoolForm key="1" suggestionPoolContext={suggestionPoolContext} />);
    } else if (rootType == "channel_vote_types") {
        var voteTypeContext = {
            isPremium: getElementValueOrNull("isPremium"),
            voteTypeAPIUrl: getElementValueOrNull("voteTypeAPIUrl"),
            voteTypeListAPIUrl: getElementValueOrNull("voteTypeListAPIUrl"),
            suggestionPoolListAPIUrl: getElementValueOrNull("suggestionPoolListAPIUrl"),
            voteStyleAPIUrl: getElementValueOrNull("voteStyleAPIUrl"),
            formSubmitUrl: getElementValueOrNull("formSubmitUrl"),
            csrfToken: getElementValueOrNull("csrfToken"),
            action: getElementValueOrNull("action"),
            error: getElementValueOrNull("error")
        };
        rootComponents.push(<VoteTypeForm key="1" voteTypeContext={voteTypeContext} />);
    } else if (rootType == "channel_shows") {
        var channelShowContext = {
            isPremium: getElementValueOrNull("isPremium"),
            showAPIUrl: getElementValueOrNull("showAPIUrl"),
            showListAPIUrl: getElementValueOrNull("showListAPIUrl"),
            voteTypeListAPIUrl: getElementValueOrNull("voteTypeListAPIUrl"),
            playerListAPIUrl: getElementValueOrNull("playerListAPIUrl"),
            formSubmitUrl: getElementValueOrNull("formSubmitUrl"),
            csrfToken: getElementValueOrNull("csrfToken"),
            action: getElementValueOrNull("action"),
            error: getElementValueOrNull("error")
        };
        rootComponents.push(<ChannelShowForm key="1" channelShowContext={channelShowContext} />);
    } else if (rootType == "show_suggestion_pool") {
        var showSuggestionPoolContext = {
            showID: getElementValueOrNull("showID"),
            suggestionPoolID: getElementValueOrNull("suggestionPoolID"),
            suggestionPoolDisplayName: getElementValueOrNull("suggestionPoolDisplayName"),
            suggestionPoolDescription: getElementValueOrNull("suggestionPoolDescription"),
            suggestingDisabled: getElementValueOrNull("suggestingDisabled"),
            isChannelAdmin: getElementValueOrNull("isChannelAdmin"),
            suggestionListAPIUrl: getElementValueOrNull("suggestionListAPIUrl"),
            suggestionPoolListAPIUrl: getElementValueOrNull("suggestionPoolListAPIUrl"),
            channelHomeUrl: getElementValueOrNull("channelHomeUrl"),
            userID: getElementValueOrNull("userID"),
            sessionID: getElementValueOrNull("sessionID"),
            formSubmitUrl: getElementValueOrNull("formSubmitUrl"),
            upvoteSubmitUrl: getElementValueOrNull("upvoteSubmitUrl"),
            csrfToken: getElementValueOrNull("csrfToken"),
            action: getElementValueOrNull("action"),
            error: getElementValueOrNull("error"),
            suggestalot: getElementValueOrNull("suggestalot")
        };
        rootComponents.push(<ShowSuggestionPool key="1" showSuggestionPoolContext={showSuggestionPoolContext} />);
    } else if (rootType == "show_controller") {
        var showControllerContext = {
            showID: getElementValueOrNull("showID"),
            showAPIUrl: getElementValueOrNull("showAPIUrl"),
            voteTypeAPIUrl: getElementValueOrNull("voteTypeAPIUrl"),
            formSubmitUrl: getElementValueOrNull("formSubmitUrl"),
            csrfToken: getElementValueOrNull("csrfToken"),
            action: getElementValueOrNull("action"),
            error: getElementValueOrNull("error")
        };
        rootComponents.push(<ShowController key="1" showControllerContext={showControllerContext} />);
    } else if (rootType == "show_display") {
        var showDisplayContext = {
            showID: getElementValueOrNull("showID"),
            teamPhotoUrl: getElementValueOrNull("teamPhotoUrl"),
            playerAPIUrl: getElementValueOrNull("playerAPIUrl"),
            suggestionAPIUrl: getElementValueOrNull("suggestionAPIUrl"),
            showAPIUrl: getElementValueOrNull("showAPIUrl"),
            liveVoteAPIUrl: getElementValueOrNull("liveVoteAPIUrl"),
            showLeaderboardAPIUrl: getElementValueOrNull("showLeaderboardAPIUrl"),
            voteTypeAPIUrl: getElementValueOrNull("voteTypeAPIUrl"),
            voteOptionAPIUrl: getElementValueOrNull("voteOptionAPIUrl"),
            channelShowLeaderboardUrl: getElementValueOrNull("channelShowLeaderboardUrl"),
        };
        rootComponents.push(<ShowDisplay key="1" showDisplayContext={showDisplayContext} />);
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