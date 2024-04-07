// Use AJAX to dynamically change site

$(document).ready(() => {
    $('.activate_key_btn').click(event => {
        event.preventDefault();
        var target = event.target.parentNode;
        const urlParams = new URLSearchParams(target.getAttribute('href'));
        console.log(urlParams.entries());
        var keyId = target.getAttribute('key_id'); 
        var action = urlParams.get('action');
        
        $.ajax({
            url: "/account?key=" + encodeURIComponent(keyId) + "&action=" + encodeURIComponent(action),
            type: "POST", 
            success: response => {
                if (action === 'activate') {
                    if (event.target.classList.contains('fa-toggle-on')) {
                        event.target.classList.remove('fa-toggle-on');
                        event.target.classList.add('fa-toggle-off');
                        event.target.parentElement.parentElement
                                .previousElementSibling.firstChild.innerHTML = 'Inactive';
                    } else {
                        event.target.classList.remove('fa-toggle-off');
                        event.target.classList.add('fa-toggle-on');
                        event.target.parentElement.parentElement
                                .previousElementSibling.firstChild.innerHTML = 'Active';
                    }   
                }
            }, error: function(xhr, status, error) {
                console.error("Error: ", status, error);
            }
        });
    });
    // Edit apikey name coming soon
    $('.del_key_btn').click(event => {
        event.preventDefault();
        const urlParams = event.target.getAttribute('href');
        $.ajax({
            url: urlParams,
            type: "POST",
            success: response => {
                to_delete_node = event.target.parentNode.parentNode;
                to_delete_node.parentNode.removeChild(to_delete_node);
            }
        });
        
    });
});