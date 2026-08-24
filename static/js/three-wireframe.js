/* ==========================================================================
   THREE.JS 3D WIREFRAME VISUALIZER & CYBER TERMINAL SIMULATION
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    // --------------------------------------------------------------------------
    // 1. THREE.JS 3D ROTATING WIREFRAME MESH (Hero Widget & Background)
    // --------------------------------------------------------------------------
    const canvasContainer = document.getElementById('three-hero-container');
    
    if (canvasContainer && typeof THREE !== 'undefined') {
        const width = canvasContainer.clientWidth || 300;
        const height = canvasContainer.clientHeight || 160;

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
        camera.position.z = 4.5;

        const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
        renderer.setSize(width, height);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        canvasContainer.appendChild(renderer.domElement);

        // Create Wireframe Polyhedron / Octahedron & Outer Ring
        const geometry = new THREE.OctahedronGeometry(1.4, 1);
        const wireframeGeo = new THREE.WireframeGeometry(geometry);

        // Cyber Yellow Wireframe Material
        const lineMaterial = new THREE.LineBasicMaterial({
            color: 0xfacc15,
            linewidth: 1.5,
            transparent: true,
            opacity: 0.85
        });

        const meshLines = new THREE.LineSegments(wireframeGeo, lineMaterial);
        scene.add(meshLines);

        // Inner glowing core
        const coreGeo = new THREE.IcosahedronGeometry(0.6, 0);
        const coreMat = new THREE.MeshBasicMaterial({
            color: 0xffffff,
            wireframe: true,
            transparent: true,
            opacity: 0.4
        });
        const coreMesh = new THREE.Mesh(coreGeo, coreMat);
        scene.add(coreMesh);

        // Mouse interaction
        let mouseX = 0;
        let mouseY = 0;
        let targetX = 0;
        let targetY = 0;

        window.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth - 0.5) * 2;
            mouseY = (e.clientY / window.innerHeight - 0.5) * 2;
        });

        // Animation Loop
        const animate = () => {
            requestAnimationFrame(animate);

            targetX += (mouseX - targetX) * 0.05;
            targetY += (mouseY - targetY) * 0.05;

            meshLines.rotation.x += 0.008;
            meshLines.rotation.y += 0.012;
            meshLines.rotation.x += targetY * 0.02;
            meshLines.rotation.y += targetX * 0.02;

            coreMesh.rotation.x -= 0.01;
            coreMesh.rotation.y -= 0.015;

            renderer.render(scene, camera);
        };

        animate();

        // Responsive resize
        window.addEventListener('resize', () => {
            if (!canvasContainer) return;
            const newW = canvasContainer.clientWidth;
            const newH = canvasContainer.clientHeight;
            camera.aspect = newW / newH;
            camera.updateProjectionMatrix();
            renderer.setSize(newW, newH);
        });
    }

    // --------------------------------------------------------------------------
    // 2. INTERACTIVE TERMINAL SIMULATOR (Home Page)
    // --------------------------------------------------------------------------
    const termBody = document.getElementById('terminal-interactive-content');
    if (termBody) {
        // Can add interactive clicks / prompt responses
        console.log('[SYS.MV] Cyber HUD Terminal Protocol Initialized.');
    }
});
