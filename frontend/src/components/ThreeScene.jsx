import { Suspense, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Environment } from "@react-three/drei";
import Butterfly from "./Butterfly.jsx";

export default function ThreeScene() {
  const butterflies = useMemo(
    () =>
      Array.from({ length: 6 }).map((_, index) => ({
        id: index,
        position: [
          (Math.random() - 0.5) * 6,
          Math.random() * 2 + 0.5,
          Math.random() * -4 - 1.5
        ],
        speed: 0.2 + Math.random() * 0.35,
        size: 0.6 + Math.random() * 0.4
      })),
    []
  );

  return (
    <Canvas
      camera={{ position: [0, 0, 6], fov: 50 }}
      gl={{ antialias: true, alpha: true }}
    >
      <Suspense fallback={null}>
        <ambientLight intensity={0.35} />
        <directionalLight position={[4, 6, 5]} intensity={0.4} />
        <Environment preset="night" />

        {/* Each butterfly is a reusable instance with individual animation parameters */}
        {butterflies.map((props) => (
          <Butterfly key={props.id} {...props} />
        ))}

        <CameraRig />
      </Suspense>
    </Canvas>
  );
}

function CameraRig() {
  // Apply subtle camera parallax based on pointer position for depth feel.
  useFrame(({ camera, pointer }) => {
    camera.position.x += (pointer.x * 1.5 - camera.position.x) * 0.05;
    camera.position.y += (pointer.y * 0.8 - camera.position.y) * 0.05;
    camera.lookAt(0, 0, 0);
  });
  return null;
}
