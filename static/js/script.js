document.addEventListener('DOMContentLoaded', function () {
    const imagePath = '{{ url_for("static", filename="images/CAT") }}';

    const imageContainer = document.getElementById('image-container');

    fetchImages(imagePath)
        .then(images => {
            displayImages(images);
        })
        .catch(error => {
            console.error('Error fetching images:', error);
        });

    function fetchImages(path) {
        return fetch(path)
            .then(response => response.json())
            .then(data => data.images);
    }

    function displayImages(images) {
        images.forEach(image => {
            const imgElement = document.createElement('img');
            imgElement.src = imagePath + image;
            imgElement.alt = image;
            imageContainer.appendChild(imgElement);
        });
    }
});
