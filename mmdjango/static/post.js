// Do fb search for input text
function doSearch(toSearch, resultsDiv, type, onclickFunction) {
    if ($.trim(toSearch).length == 0) {
        resultsDiv.html('').hide();
        return;
    }

    FB.api('/search', {
        q: toSearch,
        type: 'page',
        fields: 'name, category, picture, link, likes',
        limit: '6'
    }, function(response) {
        // Display search results
        resultsDiv.html('').show().css('border', '1px solid black');
        $.each(response.data, function(k, v) {
            resultsDiv.append(
                '<div class="result ' + type + '" data-name="' + v.name + '" data-link="' + v.link + '">' + 
                    '<img class="resultImg" src="' + v.picture + '"></img>' +
                    '<div class="resultText"><b>' + v.name + '</b><br>' + 
                    '' + v.category + '<br>' +
                    '<small>' + v.likes + ' likes</small></div>' +
                '</div>');
        });
        
        $('div.'+type).on('click', onclickFunction);
    });
}

$(function(){
    $('p#noScript').hide();
});
    
/// SINGLE ARTIST SEARCH
$(function(){
    var typingTimer,
        doneTypingTime = 800, 
        SLIDE_TIME = 800,
        searchText = $('input#artistSearchText'),
        data = null,
        resultsDiv = $('div#artistSearchResults'),
        resultsList = $('ul#resultsList'),
        refreshLink = $('input#refreshDataLink'),
        refreshTitle = 'Re-search facebook for music data',
        recommendHeader = $('h1#recommended'),
        recommendedList = $('ul#recommendedList');
        
    // Clear or refresh results
    refreshLink.on('click', function(e) {
        if (refreshLink.val() == 'Clear') {
            e.preventDefault();
            resultsList.slideUp(SLIDE_TIME);
            recommendedList.delay(SLIDE_TIME).slideDown(SLIDE_TIME);
            resultsDiv.hide();
            refreshLink.val('Refresh').attr('title', refreshTitle);
            recommendHeader.text('Recommended music');
        }
    });
        
    function getSearchDataSingle() {
        doSearch(searchText.val(), resultsDiv, 'find', searchArtistFunction);
        
        // Select result and finds similar
        function searchArtistFunction() {
            var selected = $(this),
                name = selected.data('name');
            selected.siblings().removeClass('resultSelected').addClass('result');
            selected.addClass('resultSelected');
    //        data.picture = selected.children('img.resultImg').attr('src');
    //        data.name = selected.data('name');
    //        data.link = selected.data('link');
            if (searchText.val) {
                var relatedArtists = $.ajax({
                    url: '/api',
                    dataType: 'json',
                    data: { q: name }
                });
                
                relatedArtists.then(function(response) {
                    resultsList.html('');
                    
                    if (response.length > 0) {
                        $.each(response, function(k, artist) {
                            resultsList.append(
                                '<li>' +
                                    '<div class="artistBox">' +
			                            '<a class="artistLink" href="' + artist[1][3] + '">' +
				                        '<img class="artistPic" src="' + artist[1][2] + '">' +
				                        '<div class="artistName">' +
			                                artist[0] +
			                            '</div>' +
			                            '</a>' +
		                            '</div>' +
                                '</li>'
                            );
                        });
                    } else {
                        resultsList.append(
                            '<li>' +
                                '<p class="noResults">' +
                                    '<b>' + name + '</b> was not found in your friends music.' +
                                '</p>' +
                            '</li>'
                        );
                    }
                    
                    recommendedList.slideUp(SLIDE_TIME);
                    resultsList.delay(SLIDE_TIME).slideDown(SLIDE_TIME);
                    refreshLink.val('Clear').attr('title', 'Clear search results');
                    recommendHeader.text('Search results');
                });
            }
        }
    }
    
    // Does search after 800 ms or on button click
    $('input#artistSearchButton').on('click', getSearchDataSingle);
    searchText.keyup(function() {
        clearTimeout(typingTimer);
        if (searchText.val) {
            typingTimer = setTimeout(getSearchDataSingle, doneTypingTime);
        }
    });
});

/// SEND RECOMMENDATION
$(function(){
    $('input.postButton').click(function() {
        var button = $(this),
            searchDiv = button.parent().siblings('div.search'),
            resultsDiv = searchDiv.siblings('div.results');
        
        if (button.val() == 'Recommend music') {
            button.val('Cancel');
            
            // Add search form if it doesn't exist
            if (searchDiv.length == 0) {
                button.parent().parent().append(
                '<div class="search">' + 
                    '<div class="searchBar">' +
                        '<input type="text" class="searchText"></input>' +
                        '<input type="button" class="searchButton"></input>' +
                    '</div>' +
                '</div>' +
                '<div class="results"></div>');
                
                searchDiv = button.parent().siblings('div.search');
                resultsDiv = searchDiv.siblings('div.results');
            } else {
                searchDiv.show();
            }
            
            // Does search after 800 ms or on button click
            var typingTimer,
                doneTypingTime = 800, 
                searchText = searchDiv.find('input.searchText');
                
            function getSearchData() {
                doSearch(searchText.val(), resultsDiv, 'rec', recommendFunction);
                
                // Post to wall
                function recommendFunction() {
                    if (searchText.val) {
                        FB.ui({
                            method: 'feed',
                            to: button.data('id'),
                            display: 'popup',
                            link: $(this).data('link')
                        }, function(response) {
                        });
                    }
                }
            }
            
            searchDiv.find('input.searchButton').on('click', getSearchData);
            searchText.keyup(function() {
                clearTimeout(typingTimer);
                if (searchText.val) {
                    typingTimer = setTimeout(getSearchData, doneTypingTime);
                }
            });
            
        // If cancelling, hide search form
        } else {
            button.val('Recommend music');
            searchDiv.hide();
            resultsDiv.hide();
        }
    });
});
