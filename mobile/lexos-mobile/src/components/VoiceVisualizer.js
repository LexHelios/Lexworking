import React, { useEffect, useRef } from 'react';
import { View, Animated, StyleSheet } from 'react-native';

export const VoiceVisualizer = ({ isActive, color = '#00ff00' }) => {
  const bars = useRef([...Array(5)].map(() => new Animated.Value(0.3))).current;
  
  useEffect(() => {
    if (isActive) {
      const animations = bars.map((bar, index) => {
        return Animated.loop(
          Animated.sequence([
            Animated.timing(bar, {
              toValue: Math.random() * 0.7 + 0.3,
              duration: 200 + index * 50,
              useNativeDriver: true,
            }),
            Animated.timing(bar, {
              toValue: 0.3,
              duration: 200 + index * 50,
              useNativeDriver: true,
            }),
          ])
        );
      });
      
      Animated.parallel(animations).start();
    } else {
      bars.forEach(bar => {
        Animated.timing(bar, {
          toValue: 0.3,
          duration: 200,
          useNativeDriver: true,
        }).start();
      });
    }
  }, [isActive]);
  
  return (
    <View style={styles.container}>
      {bars.map((bar, index) => (
        <Animated.View
          key={index}
          style={[
            styles.bar,
            {
              backgroundColor: color,
              transform: [{ scaleY: bar }],
            },
          ]}
        />
      ))}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    height: 50,
    width: 100,
  },
  bar: {
    width: 4,
    height: 40,
    marginHorizontal: 3,
    borderRadius: 2,
  },
});