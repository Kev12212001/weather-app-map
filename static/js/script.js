    <script>
        // Predefined list of map images
        const mapImages = [
            '620sfc.png', 
            '620p.png', 
            '620t.png', 
            '620d.png', 
            '620uv.png', 
            '620aqi.png', 
            '620cc.png'
        ];

        let currentIndex = 0; // Start at the first image

        const imgElement = document.getElementById('map-image');
        const nextBtn = document.getElementById('next-btn');
        const prevBtn = document.getElementById('prev-btn');

        // Function to update the image source based on the current index
        function updateImage() {
            imgElement.src = mapImages[currentIndex];
        }

        // Handle next button click
        nextBtn.addEventListener('click', function() {
            currentIndex++;
            if (currentIndex >= mapImages.length) currentIndex = 0; // Loop back to the first image
            updateImage();
        });

        // Handle previous button click
        prevBtn.addEventListener('click', function() {
            currentIndex--;
            if (currentIndex < 0) currentIndex = mapImages.length - 1; // Loop back to the last image
            updateImage();
        });

        // Enable arrow key navigation for the maps
        document.addEventListener('keydown', function(event) {
            const key = event.key;
            if (key === 'ArrowRight') {
                currentIndex++;
                if (currentIndex >= mapImages.length) currentIndex = 0; // Loop back to the first image
                updateImage();
            } else if (key === 'ArrowLeft') {
                currentIndex--;
                if (currentIndex < 0) currentIndex = mapImages.length - 1; // Loop back to the last image
                updateImage();
            }
        });
    </script>