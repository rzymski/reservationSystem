function getCookie(name) {
    // Function to retrieve a cookie value by name
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}
// function passDataByAJAXUniversal(url, data) {
//     console.log("UNIVERSAL OSTATECZNY URL =", url, "DATA =", data)
//     const csrfToken = getCookie('csrftoken');
//     $.ajax({
//         type: 'POST',
//         url: url,
//         headers: {
//             'X-CSRFToken': csrfToken
//         },
//         data: data,
//         success: function(response) {
//             console.error("SUCCESS ajax = ", response)
//             return response;
//         },
//         error: function (response) {
//             console.error("ERROR ajax = ", response)
//             return response;
//         }
//     });
// };

function passDataByAJAXUniversal(url, data) {
    console.log("UNIVERSAL OSTATECZNY URL =", url, "DATA =", data)
    return new Promise(function(resolve) {
        const csrfToken = getCookie('csrftoken');
        $.ajax({
            type: 'POST',
            url: url,
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: data,
            success: function(response) {
                console.error("SUCCESS ajax = ", response)
                resolve(response);
            },
            error: function (response) {
                console.error("ERROR ajax = ", response)
                resolve(response);
            }
        });
    });
};