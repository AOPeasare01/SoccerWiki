function shareOnFacebook() {
    const pageUrl = encodeURIComponent(window.location.href);
    window.open(`https://www.facebook.com/sharer/sharer.php?u=${pageUrl}`, '_blank');
}

function shareOnTwitter() {
    const pageUrl = encodeURIComponent(window.location.href);
    const pageTitle = encodeURIComponent(document.title); // Optional: Include the page title in the tweet
    window.open(`https://twitter.com/intent/tweet?text=${pageTitle}&url=${pageUrl}`, '_blank');
}

function shareOnLinkedIn() {
    const pageUrl = encodeURIComponent(window.location.href);
    window.open(`https://www.linkedin.com/shareArticle?mini=true&url=${pageUrl}`, '_blank');
}

