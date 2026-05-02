import os

files = [
    r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\templates\users\home.html',
    r'c:\Users\91894\OneDrive\Desktop\AWT\art_gallery\templates\users\buyer_dashboard.html'
]

modal_html = '''
    <!-- ARTWORK MODAL -->
    <div id="artworkModal" class="artwork-modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <div class="modal-frame">
                <img id="modalImage" src="" alt="Artwork">
            </div>
            <div class="modal-info">
                <h3 id="modalTitle">Title</h3>
                <p id="modalArtist" style="color: var(--primary); font-size: 14px; margin-bottom: 10px;">Artist</p>
                <div id="modalDesc" style="color: var(--text-muted); font-size: 15px; line-height: 1.6; margin-bottom: 20px;"></div>
                <div id="modalPrice" class="price" style="font-size: 24px; font-weight: bold; margin-bottom: 20px;"></div>
                <div id="modalActions"></div>
            </div>
        </div>
    </div>
'''

modal_css = '''
        /* ARTWORK MODAL STYLES */
        .artwork-modal {
            display: none;
            position: fixed;
            z-index: 2000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            overflow: auto;
            background-color: rgba(0,0,0,0.85);
            backdrop-filter: blur(10px);
            opacity: 0;
            transition: opacity 0.4s ease;
        }

        .artwork-modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
            opacity: 1;
        }

        .modal-content {
            background: rgba(20, 20, 20, 0.95);
            margin: auto;
            padding: 40px;
            border: 1px solid var(--glass-border);
            width: 80%;
            max-width: 1000px;
            border-radius: 20px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.8);
            display: flex;
            gap: 40px;
            position: relative;
            transform: scale(0.9);
            transition: transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }

        .artwork-modal.show .modal-content {
            transform: scale(1);
        }

        .close-modal {
            color: #aaa;
            position: absolute;
            top: 20px;
            right: 30px;
            font-size: 38px;
            font-weight: bold;
            cursor: pointer;
            transition: 0.3s;
        }

        .close-modal:hover {
            color: #fff;
        }

        .modal-frame {
            flex: 1;
            padding: 20px;
            background: #111;
            /* GOLDEN FRAME EFFECT */
            border: 24px solid transparent;
            border-image: linear-gradient(to bottom right, #e6c55d, #b38b22, #ffe58f, #8a6314) 1;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8), 0 20px 40px rgba(0,0,0,0.6);
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-frame img {
            max-width: 100%;
            max-height: 60vh;
            object-fit: contain;
            box-shadow: 0 10px 20px rgba(0,0,0,0.5);
        }

        .modal-info {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }

        @media (max-width: 768px) {
            .modal-content {
                flex-direction: column;
                padding: 20px;
                gap: 20px;
            }
        }
'''

modal_js = '''
        // MODAL LOGIC
        function openModal(title, artist, desc, price, imgUrl, itemId, status, isBuyer) {
            const modal = document.getElementById('artworkModal');
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalArtist').textContent = 'by ' + artist;
            document.getElementById('modalDesc').textContent = desc || 'An exclusive masterpiece available on Artify.';
            document.getElementById('modalPrice').textContent = '₹' + price;
            document.getElementById('modalImage').src = imgUrl;
            
            let actionsObj = document.getElementById('modalActions');
            if(actionsObj && isBuyer && status === 'available') {
                actionsObj.innerHTML = `<button class="btn btn-primary" onclick="addToCart(${itemId}, '${title.replace(/'/g, "\\'")}', ${price}, '${imgUrl}')">Add to Cart</button>`;
            } else if (actionsObj && isBuyer) {
                actionsObj.innerHTML = `<div style="background: rgba(239, 68, 68, 0.1); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.2); padding: 8px 16px; border-radius: 20px; display: inline-block; font-size: 14px; font-weight: 700; text-transform: uppercase;">Sold Out</div>`;
            }

            modal.style.display = 'flex';
            setTimeout(() => { modal.classList.add('show'); }, 10);
        }

        function closeModal() {
            const modal = document.getElementById('artworkModal');
            modal.classList.remove('show');
            setTimeout(() => { modal.style.display = 'none'; }, 400);
        }

        window.onclick = function(event) {
            const modal = document.getElementById('artworkModal');
            if (event.target == modal) {
                closeModal();
            }
        }
'''

for path in files:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'id="artworkModal"' not in content:
            # insert CSS
            content = content.replace('</style>', modal_css + '\n    </style>')
            # insert HTML
            content = content.replace('</body>', modal_html + '\n</body>')
            # insert JS
            content = content.replace('</script>', modal_js + '\n    </script>')
            # For home, if script isn't found, insert at bottom
            if '</script>' not in content and 'function closeModal' not in content:
                content = content.replace('</body>', '<script>\n' + modal_js + '\n</script>\n</body>')
                
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
