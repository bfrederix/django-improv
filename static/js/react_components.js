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

function showDateFormat(stringDate) {
    return moment.utc(stringDate).format("ddd. MMM. Do, YYYY @hA");
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

///////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////// BASE COMPONENTS /////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////////////////

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
    var formClass = "form-" + this.props.formStyle;
    return (
      <form className={formClass} role="form"
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
        docs = <a href={this.props.docs}>Explained Here</a>;
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
    var panelClasses = 'panel panel-' + this.props.panelColor + ' panel-shadow';
    var panelComponents = [];
    if (this.props.panelHeadingContent) {
        panelComponents.push(<PanelHeader key="1"
                                          panelHeadingClasses={this.props.panelHeadingClasses}
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
    var panelHeaderClasses = 'panel-heading ' + this.props.panelHeadingClasses + " panel-heading-shadow";
    if (this.props.panelHeadingLink) {
        link = <span>(<a href={this.props.panelHeadingLink}>Read More</a>)</span>;
    }
    return (
      <div className={panelHeaderClasses}>{this.props.panelHeadingContent} {link}</div>
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
    if (!this.state.data){
        return (<Loading loadingBarColor="#fff" />);
    }
    return (
      <img src={this.state.data.photo_url} className="img-responsive img-thumbnail" />
    );
  }
});

var Image = React.createClass({
  render: function() {
    return (
      <img src={this.props.image_url} className="img-responsive img-thumbnail" />
    );
  }
});

var BigButton = React.createClass({
  render: function() {
    var buttonClass = "btn btn-" + this.props.buttonColor + " btn-block btn-lg text-center x-large-font btn-shadow";
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
            var showDateFormatted = showDateFormat(show.created);
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
    var buttonClass = "btn btn-" + buttonColor + " btn-block btn-lg dropdown-toggle x-large-font btn-shadow";

    return (
        <div className="row">
            <div className="col-md-6 col-md-offset-3">
                <div className="btn-group" style={buttonGroupStyle}>
                  <button className={buttonClass} data-toggle="dropdown" aria-expanded="false">
                    {this.props.currentSelection}&nbsp;<span className="caret "></span>
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
    if (!this.state.data){
        return (<div>
                    <Loading loadingBarColor="#fff"/>
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
        optionList.push(<option key={this.counter} value={item.id}>{item.name}</option>);
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
      limitFileSize(event, 'logoFile');
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
    // Name Input
    var nameInput = <input type="text" id="name" name="name" defaultValue={this.state.data.name} className="form-control"></input>;
    formContents.push(<FormGroup key="1"
                                 labelSize="2"
                                 labelContents="*Url Name:"
                                 inputSize="5"
                                 input={nameInput}
                                 helpBlock="Required: Used as the url address and can only be letters, numbers, hyphens or underscores" />);
    // Display Name Input
    var displayNameInput = <input type="text" id="display_name" name="display_name" defaultValue={this.state.data.display_name} className="form-control"></input>;
    formContents.push(<FormGroup key="2"
                                 labelSize="2"
                                 labelContents="*Display Name:"
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
    // Logo Image Input
    var logoInput = <div><span className="btn btn-primary btn-file"><input id="logoFile" type="file" name="logoFile"></input></span><Image image_url={this.state.data.logo_url} /></div>;
    formContents.push(<FormGroup key="5"
                                 labelSize="2"
                                 labelContents="Logo Image:"
                                 inputSize="3"
                                 input={logoInput}
                                 helpBlock="Used during shows, must be smaller than 2MB" />);

    // Team Photo Input
    var teamPhotoInput = <div><span className="btn btn-primary btn-file"><input id="teamPhotoFile" type="file" name="teamPhotoFile"></input></span><Image image_url={this.state.data.team_photo_url} /></div>;
    formContents.push(<FormGroup key="6"
                                 labelSize="2"
                                 labelContents="Team Photo:"
                                 inputSize="3"
                                 input={teamPhotoInput}
                                 helpBlock="Used on the channel's about page, must be smaller than 2MB" />);
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
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow">{actionText}</button>;
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
            <FormLabel action={this.props.channelCreateEditContext.action}
                       error={this.props.channelCreateEditContext.error} />
            <Panel panelWidth="6" panelOffset="3" panelColor="info"
                   panelHeadingContent={actionText} panelHeadingClasses="x-large-font"
                   panelBodyClasses="white-background"
                   panelHeadingLink="http://improvote.readthedocs.org/en/latest/channels.html"
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
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow">Create/Edit Player</button>;
    formContents.push(<FormGroup key="5"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Player Dropdown Input
    var playerEditInput = <DropDownSelect listAPIUrl={this.props.addPlayerContext.playerListAPIUrl}
                                          selectEventHandler={this.handleEditPlayer}
                                          selectID="playerID"
                                          defaultSelected={this.state.editPlayerID}
                                          defaultText="Select a Player to Edit" />;
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
                   panelHeadingLink="http://improvote.readthedocs.org/en/latest/players.html"
                   bodyContent={bodyContent} />
        </div>
    );
  }
});


var SuggestionPoolForm = React.createClass({
  getInitialState: function() {
    return {data: {name: "",
                   display_name: "",
                   description: 'Instructive text used to help guide users on what suggestions to enter',
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
                                 helpBlock="Used to instruct users on what types of suggestions to enter"
                                 docs="http://improvote.readthedocs.org/en/latest/suggestion_pools.html#suggestion-pool-description" />);
    // Max User Suggestions Input
    var maxUserSuggestionsInput = <input type="text" id="max_user_suggestions" name="max_user_suggestions" maxLength="3" defaultValue={this.state.data.max_user_suggestions} className="form-control"></input>;
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="User Suggestion Limit*:"
                                 inputSize="2"
                                 input={maxUserSuggestionsInput}
                                 helpBlock="How many suggestions each user can enter for this suggestion pool" />);
    // Admin Only Input
    var adminOnlyInput = <input type="checkbox" name="admin_only" value="1" defaultChecked={this.state.data.admin_only}></input>;
    formContents.push(<FormGroup key="5"
                                 labelSize="2"
                                 labelContents="Admin Suggestions Only:"
                                 inputSize="4"
                                 input={adminOnlyInput}
                                 helpBlock="Check this if only admin can enter suggestions in this pool" />);
    // Require Login Input
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
                                 helpBlock="Check this if users are required to login to add suggestions (premium only feature)" />);
    // Active Input
    var activeInput = <input type="checkbox" name="active" value="1" defaultChecked={this.state.data.active}></input>;
    formContents.push(<FormGroup key="7"
                                 labelSize="2"
                                 labelContents="Suggestion Pool Active:"
                                 inputSize="4"
                                 input={activeInput}
                                 helpBlock="Check this if the Suggestion Pool should appear in the Create/Edit Vote Types form" />);
    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow">Create/Edit Suggestion Pool</button>;
    formContents.push(<FormGroup key="8"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Suggestion Pool Dropdown Input
    var suggestionPoolEditInput = <DropDownSelect listAPIUrl={this.props.suggestionPoolContext.suggestionPoolListAPIUrl}
                                                  selectEventHandler={this.editEventHandler}
                                                  defaultSelected={this.state.suggestionPoolID}
                                                  defaultText="Select a Suggestion Pool to Edit" />;
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
                   panelHeadingLink="http://improvote.readthedocs.org/en/latest/suggestion_pools.html"
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
                   preshow_voted: false,
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
    // Suggestion Pool Dropdown Input
    var suggestionPoolInput = <DropDownSelect listAPIUrl={this.props.voteTypeContext.suggestionPoolListAPIUrl}
                                              defaultSelected={this.state.data.suggestion_pool}
                                              defaultText="Select a Suggestion Pool" />;
    formContents.push(<FormGroup key="3"
                                 labelSize="2"
                                 labelContents="Suggestion Pool:"
                                 inputSize="5"
                                 input={suggestionPoolInput}
                                 helpBlock="Select a Suggestion Pool if the vote type requires suggestions (active suggestion pools only)" />);
    // Pre-show Voted Input
    var preshowVotedInput = <input type="checkbox" name="preshow_voted" value="1" defaultChecked={this.state.data.preshow_voted}></input>;
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="Disallow Audience Voting:"
                                 inputSize="5"
                                 input={preshowVotedInput}
                                 helpBlock="Check this if the winner should be automatically selected instead of allowing the audience to vote" />);
    // Intervals Input
    var intervalsInput = <input type="text" id="intervals" name="intervals" defaultValue={this.state.data.intervals} className="form-control"></input>;
    formContents.push(<FormGroup key="5"
                                 labelSize="2"
                                 labelContents="Intervals:"
                                 inputSize="6"
                                 input={intervalsInput}
                                 helpBlock="Used to specify minute intervals at which votes are introduced into the show. Must begin with 0. (ex. 0,3,6,8,9,10)" />);
    // Manual Interval Control Input
    var manualIntervalControlInput = <input type="checkbox" name="manual_interval_control" value="1" defaultChecked={this.state.data.manual_interval_control}></input>;
    formContents.push(<FormGroup key="6"
                                 labelSize="2"
                                 labelContents="Manual Interval Voting Control:"
                                 inputSize="5"
                                 input={manualIntervalControlInput}
                                 helpBlock='Check this if you want the "tech" to control when interval voting occurs' />);
    // Style Dropdown Input
    var styleInput = <DropDownSelect listAPIUrl={this.props.voteTypeContext.voteStyleAPIUrl}
                                     defaultSelected={this.state.data.style}
                                     defaultText="Select a Voting Style"
                                     selectID="style" />;
    formContents.push(<FormGroup key="7"
                                 labelSize="2"
                                 labelContents="Voting Style:"
                                 inputSize="6"
                                 input={styleInput}
                                 helpBlock='Select a voting style for the Vote Type.'
                                 docs="http://improvote.readthedocs.org/en/latest/vote_types.html#vote-styles" />);
    // ordering Input
    var orderingInput = <input type="text" id="ordering" name="ordering" maxLength="2" defaultValue={this.state.data.ordering} className="form-control"></input>;
    formContents.push(<FormGroup key="8"
                                 labelSize="2"
                                 labelContents="Order:"
                                 inputSize="4"
                                 input={orderingInput}
                                 helpBlock='The numeric order in which the voting types appear, either as buttons on the Show Control page, or otherwise.' />);
    // options Input
    var optionsInput = <input type="text" id="options" name="options" maxLength="1" defaultValue={this.state.data.options} className="form-control"></input>;
    formContents.push(<FormGroup key="9"
                                 labelSize="2"
                                 labelContents="Voting Options:"
                                 inputSize="4"
                                 input={optionsInput}
                                 helpBlock='The number of voting options that appear on the voting page. Make sure you choose a number that will fit on the Show Display screen' />);
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
    var buttonColorInput = <input type="color" name="button_color" defaultValue={this.state.data.button_color} className="form-control"></input>;
    formContents.push(<FormGroup key="12"
                                 labelSize="2"
                                 labelContents="Vote Type Color:"
                                 inputSize="4"
                                 input={buttonColorInput}
                                 helpBlock='The color designated to the Vote Type buttons and such' />);
    // Require Login Input
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
                                 helpBlock="Check this if users are required to login to vote (premium only feature)" />);
    // Active Input
    var activeInput = <input type="checkbox" name="active" value="1" defaultChecked={this.state.data.active}></input>;
    formContents.push(<FormGroup key="14"
                                 labelSize="2"
                                 labelContents="Vote Type Active:"
                                 inputSize="5"
                                 input={activeInput}
                                 helpBlock="Check this if the Vote Type should appear in the Create Show form" />);
    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow">Create/Edit Suggestion Pool</button>;
    formContents.push(<FormGroup key="15"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Vote Type Dropdown Input
    var voteTypeEditInput = <DropDownSelect listAPIUrl={this.props.voteTypeContext.voteTypeListAPIUrl}
                                            selectEventHandler={this.editEventHandler}
                                            defaultSelected={this.state.voteTypeID}
                                            defaultText="Select a Vote Type to Edit" />;
    formContents.push(<FormGroup key="16"
                                 labelSize="2"
                                 labelContents="Edit VoteType:"
                                 inputSize="4"
                                 input={voteTypeEditInput}
                                 helpBlock="Select a Suggestion Pool if you wish to edit it" />);

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
                   panelHeadingLink="http://improvote.readthedocs.org/en/latest/vote_types.html"
                   bodyContent={bodyContent} />
        </div>
    );
  }
});


var ChannelShowForm = React.createClass({
  getInitialState: function() {
    return {data: {show_length: 150,
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

    // Only change players and vote types during creation
    if (!this.state.showID) {
        // Players Dropdown Input
        var playersInput = <DropDownSelect listAPIUrl={this.props.channelShowContext.playerListAPIUrl}
                                           selectID="players"
                                           multiple="true" />;
        formContents.push(<FormGroup key="1"
                                     labelSize="2"
                                     labelContents="Players:"
                                     inputSize="6"
                                     input={playersInput}
                                     helpBlock='Select Players for the Show' />);
        // Vote Types Dropdown Input
        var voteTypesInput = <DropDownSelect listAPIUrl={this.props.channelShowContext.voteTypeListAPIUrl}
                                             selectID="vote_types"
                                             multiple="true" />;
        formContents.push(<FormGroup key="2"
                                     labelSize="2"
                                     labelContents="Vote Types:"
                                     inputSize="6"
                                     input={voteTypesInput}
                                     helpBlock='Select Vote Types for the Show' />);
    }

    // Youtube Input
    var showLengthInput = <input type="text" id="show_length" name="show_length" defaultValue={this.state.data.show_length} className="form-control"></input>;
    formContents.push(<FormGroup key="3"
                                 labelSize="2"
                                 labelContents="Show Display Length (minutes)*:"
                                 inputSize="6"
                                 input={showLengthInput}
                                 helpBlock="Length of the show display from creation until end in minutes (should be a large overestimate of minutes, not exact), required for knowing when the show display should end and channel functionality should return to normal."
                                 docs="http://improvote.readthedocs.org/en/latest/shows.html#show-length" />);

    // Photo Link Input
    var photoLinkInput = <div><span className="btn btn-primary btn-file"><input id="photoFile" type="file" name="photoFile"></input></span><Image image_url={this.state.data.photo_link} /></div>;
    formContents.push(<FormGroup key="4"
                                 labelSize="2"
                                 labelContents="Show Photo:"
                                 inputSize="6"
                                 input={photoLinkInput}
                                 helpBlock="Photo from the show (can be added later), must be smaller than 2MB" />);

    // Youtube Input
    var youtubeInput = <input type="text" id="embedded_youtube" name="embedded_youtube" defaultValue={this.state.data.embedded_youtube} className="form-control"></input>;
    formContents.push(<FormGroup key="5"
                                 labelSize="2"
                                 labelContents="Youtube Url:"
                                 inputSize="6"
                                 input={youtubeInput}
                                 helpBlock="Youtube video from the show (can be added later), must be a valid Youtube url" />);

    // Submit Button
    var submitButton = <button type="submit" className="btn btn-danger btn-shadow">Create/Edit Show</button>;
    formContents.push(<FormGroup key="6"
                                 inputSize="2"
                                 input={submitButton} />);
    // Edit Show Dropdown Input
    var showEditInput = <DropDownSelect listAPIUrl={this.props.channelShowContext.showListAPIUrl}
                                        selectEventHandler={this.editEventHandler}
                                        defaultSelected={this.state.showID}
                                        defaultText="Select a Show to Edit" />;
    formContents.push(<FormGroup key="7"
                                 labelSize="2"
                                 labelContents="Edit Show:"
                                 inputSize="4"
                                 input={showEditInput}
                                 helpBlock="Select a Show if you wish to edit it" />);

    var bodyContent = <Form formStyle="horizontal"
                            formSubmitUrl={this.props.channelShowContext.formSubmitUrl}
                            formContents={formContents}
                            onFormSubmit={this.onFormSubmit}
                            csrfToken={this.props.channelShowContext.csrfToken} />
    return (
        <div key={this.state.key}>
            <FormLabel action={this.props.channelShowContext.action}
                       error={this.props.channelShowContext.error} />
            <Panel panelWidth="6" panelOffset="3" panelColor="info"
                   panelHeadingContent="Create/Edit/Delete Shows" panelHeadingClasses="x-large-font"
                   panelBodyClasses="white-background"
                   panelHeadingLink="http://improvote.readthedocs.org/en/latest/shows.html"
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
                            <input type="submit" className="btn btn-warning btn-block btn-lg x-large-font btn-shadow" value="Award Medals"></input>
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
        return (<div className="table-responsive">
                    <table className="table table-condensed black-font">
                        <tbody><tr><td>
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
        tableList.push(<tr key={this.counter}>
                            <td>{rank}</td>
                            <td><a href={userUrl}>{leaderboardUser.username}</a></td>
                            <td>{leaderboardUser.suggestion_wins}</td>
                            <td>{leaderboardUser.points}</td>
                            <td>{leaderboardUser.show_wins}</td>
                       </tr>);
        return tableList;
    }, this);
    return (
        <div className="table-responsive">
            <table className="table table-condensed large-font">
                <thead>
                    <tr>
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
        return (<div className="table-responsive">
                    <table className="table table-condensed black-font">
                        <tbody><tr><td>
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
        tableList.push(<tr key={this.counter}>
                            <td>{rank}</td>
                            <td><a href={userUrl}>{leaderboardUser.username}</a></td>
                            <td>{leaderboardUser.wins}</td>
                            <td>{leaderboardUser.points}</td>
                            <td>{medalList}</td>
                       </tr>);
        return tableList;
    }, this);
    return (
        <div className="table-responsive">
            <br/>
            <table className="table table-condensed large-font">
                <thead>
                    <tr>
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
        <div className="table-responsive">
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
    var showDateFormatted = showDateFormat(this.state.data.created);
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
        } else if (suggestion.voted_on === true) {
            suggestionClass = "info";
        } else {
            suggestionClass = "active";
        }
        var suggestionUrl = "/" + this.props.showStats.channel_name + "/recaps/show/" + showID + "/#" + suggestion.id;
        // If the suggestion was voted on during the show
        if (suggestion.used === true) {
            suggestionDisplay = <td className={suggestionClass}>{suggestion.value}<StarImage /></td>;
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
        var photoBodyContent = <div className="text-center"><img src={this.state.data.photo_link} className="img-responsive img-thumbnail" /></div>;
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
        var suggestionClass = "btn " + buttonClass + " btn-block large-font vote-option btn-shadow";
        var suggestionCount = i + 1;
        suggestionList.push(<div key={i} id={suggestion.id} className={suggestionClass}>
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
                                               playerID={recapItem.player} />
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
////////////////////////////////// SHOW DISPLAY COMPONENTS ///////////////////////////////
//////////////////////////////////////////////////////////////////////////////////////////

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
        } else if (state == "options") {

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
    // Make sure the current state exists and has intervals
    if (this.state.data && this.state.data.intervals !== "") {
        var buttonStyle = {backgroundColor: this.state.data.button_color};
        return (
            <button className="btn btn-block btn-lg white-input x-large-font btn-shadow" style={buttonStyle}>{this.state.data.display_name} Remaining: {this.state.data.remaining_intervals}</button>
        );
    } else {
        return (<div></div>);
    }
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
            channelID: getElementValueOrNull("channelID"),
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
            channelID: getElementValueOrNull("channelID"),
            channelName: getElementValueOrNull("channelName"),
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
            channelID: getElementValueOrNull("channelID"),
            channelName: getElementValueOrNull("channelName"),
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
            channelID: getElementValueOrNull("channelID"),
            channelName: getElementValueOrNull("channelName"),
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
            channelID: getElementValueOrNull("channelID"),
            channelName: getElementValueOrNull("channelName"),
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