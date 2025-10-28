import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import PropTypes from "prop-types";
import * as THREE from "three";

const wingMaterial = new THREE.MeshStandardMaterial({
  color: new THREE.Color("#ff4e8a"),
  emissive: new THREE.Color("#4f5bd5"),
  emissiveIntensity: 0.45,
  transparent: true,
  opacity: 0.85,
  side: THREE.DoubleSide
});

/**
 * Butterfly
 * ---------
 * Simple procedural butterfly using two planes as wings.
 * We animate wings with a sine wave and move the butterfly along a bezier-like path.
 */
export default function Butterfly({ position, speed, size }) {
  const leftWing = useRef();
  const rightWing = useRef();
  const group = useRef();

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed;
    const flap = Math.sin(t * 10) * Math.PI * 0.35;

    if (leftWing.current && rightWing.current) {
      leftWing.current.rotation.y = flap;
      rightWing.current.rotation.y = -flap;
    }

    if (group.current) {
      const oscillation = Math.sin(t * 1.2) * 0.5;
      group.current.position.x = position[0] + Math.sin(t) * 1.8;
      group.current.position.y = position[1] + Math.sin(t * 1.5) * 0.5 + oscillation;
      group.current.position.z = position[2] + Math.cos(t) * 0.6;
      group.current.rotation.y = Math.sin(t) * 0.3;
    }
  });

  return (
    <group ref={group} position={position} scale={size}>
      <mesh ref={leftWing} material={wingMaterial}>
        <planeGeometry args={[1.2, 0.9]} />
      </mesh>
      <mesh ref={rightWing} position={[0, 0, 0]} material={wingMaterial}>
        <planeGeometry args={[1.2, 0.9]} />
      </mesh>

      <mesh position={[0, -0.05, 0]}>
        <cylinderGeometry args={[0.05, 0.05, 0.8, 16]} />
        <meshStandardMaterial color="#f5f5f5" emissive="#d62976" emissiveIntensity={0.25} />
      </mesh>
    </group>
  );
}

Butterfly.propTypes = {
  position: PropTypes.arrayOf(PropTypes.number).isRequired,
  speed: PropTypes.number.isRequired,
  size: PropTypes.number.isRequired
};
