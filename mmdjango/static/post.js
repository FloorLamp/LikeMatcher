// Do fb search for input text
function doSearch(toSearch, resultsDiv) {
    if ($.trim(toSearch).length == 0) {
        resultsDiv.html('').hide();
        return null;
    }

    var data = {name: null, picture: null, link: null};
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
                '<div class="result" data-name="' + v.name + '" data-link="' + v.link + '">' + 
                    '<img class="resultImg" src="' + v.picture + '"></img>' +
                    '<div class="resultText"><b>' + v.name + '</b><br>' + 
                    '' + v.category + '<br>' +
                    '<small>' + v.likes + ' likes</small></div>' +
                '</div>');
        });
        
        // Select result
        $('div.result').on('click', function() {
            var selected = $(this);
            selected.siblings().removeClass('resultSelected').addClass('result');
            selected.addClass('resultSelected');
            data.picture = selected.children('img.resultImg').attr('src');
            data.name = selected.data('name');
            data.link = selected.data('link');
        });
    });
    return data;
}
    
/// SINGLE ARTIST SEARCH
$(function(){
    var typingTimer,
        doneTypingTime = 800, 
        SLIDE_TIME = 800,
        searchText = $('input#artistSearchText'),
        findSimilarButton = $('input#findSimilarButton'),
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
        data = doSearch(searchText.val(), resultsDiv);
    }
    
    // Does search after 800 ms or on button click
    $('input#artistSearchButton').on('click', getSearchDataSingle);
    searchText.keyup(function() {
        clearTimeout(typingTimer);
        if (searchText.val) {
            typingTimer = setTimeout(getSearchDataSingle, doneTypingTime);
        }
    });
    
    findSimilarButton.on('click', function() {
        if (searchText.val) {
            var relatedArtists = $.ajax({
                url: '/api',
                dataType: 'json',
                data: { q: data.name }
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
                                '<b>' + data.name + '</b> was not found in your friends music.' +
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
    });
});

/// SEND RECOMMENDATION
$(function(){
    $('input.postButton').click(function() {
        var button = $(this),
            searchDiv = button.parent().siblings('div.search'),
            resultsDiv = searchDiv.siblings('div.results'),
            sendPostButton = searchDiv.children('input.sendPost');
        
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
                    '<input type="button" class="sendPost button" value="Send"></input></div>' +
                '<div class="results"></div>');
                
                searchDiv = button.parent().siblings('div.search');
                resultsDiv = searchDiv.siblings('div.results');
                sendPostButton = searchDiv.children('input.sendPost');
            } else {
                searchDiv.show();
            }
            
            // Does search after 800 ms or on button click
            var typingTimer,
                doneTypingTime = 800, 
                searchText = searchDiv.find('input.searchText'),
                data = null;
                
            function getSearchData() {
                data = doSearch(searchText.val(), resultsDiv);
            }
            
            searchDiv.find('input.searchButton').on('click', getSearchData);
            searchText.keyup(function() {
                clearTimeout(typingTimer);
                if (searchText.val) {
                    typingTimer = setTimeout(getSearchData, doneTypingTime);
                }
            });
            
            // Post to wall
            sendPostButton.on('click', function() {
                if (data != null) {
                    console.log(data.link)
                    FB.ui({
                        method: 'feed',
                        to: button.data('id'),
//                        message: 'I recommend you...',
                        display: 'popup',
                        link: data.link
                    }, function(response) {
                        console.log(response);  
                    });
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
