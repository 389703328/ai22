<template>
  <div class="home">
    <h1>Welcome to Vue 3 + FastAPI</h1>
    <p>This is a full-stack application with Vue 3 frontend and FastAPI backend.</p>
    <div class="features">
      <h3>Features:</h3>
      <ul>
        <li>User Management</li>
        <li>AI Chat Interface</li>
        <li>RESTful API</li>
        <li>Modern Vue 3 Composition API</li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Home'
}
</script>

<style scoped>
* {
  box-sizing: border-box;
}

.home {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 20px;
  animation: fadeIn 0.6s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

h1 {
  font-size: 40px;
  font-weight: 700;
  margin: 0 0 20px 0;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

p {
  font-size: 18px;
  color: #666;
  line-height: 1.6;
}

.features {
  margin-top: 50px;
  background: white;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  animation: slideUp 0.5s ease-out 0.2s both;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.features h3 {
  font-size: 24px;
  color: #333;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  gap: 10px;
}

.features h3::before {
  content: '';
  width: 4px;
  height: 24px;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  border-radius: 2px;
}

.features ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.features li {
  padding: 16px;
  background: linear-gradient(135deg, #f5f7fa 0%, #f0f0f5 100%);
  border-radius: 8px;
  color: #333;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
}

.features li::before {
  content: '✓';
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #1E3C72 0%, #2A5298 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
  flex-shrink: 0;
}

.features li:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(30, 60, 114, 0.15);
  background: linear-gradient(135deg, #f0f0f8 0%, #e8e8f0 100%);
}

@media (max-width: 768px) {
  .home {
    padding: 24px 16px;
  }

  h1 {
    font-size: 28px;
  }

  .features {
    padding: 24px;
  }

  .features h3 {
    font-size: 20px;
  }

  .features ul {
    grid-template-columns: 1fr;
  }
}
</style>