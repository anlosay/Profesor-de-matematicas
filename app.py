import streamlit as st
import google.generativeai as genai
import os
from PIL import Image

# 📌 Configurar la clave de API de Gemini desde Streamlit Secrets
api_key = st.secrets["GEMINI_API_KEY"]

if not api_key:
    st.error("No se encontró la clave de API de Gemini.")
else:
    genai.configure(api_key=api_key)

# 📌 Configuración del chatbot
generation_config = {
    "temperature": 0.8,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 8192,
}

# 📌 Instrucciones personalizadas del chatbot (TU PROMPT)
system_instruction = """
📍 LIMITACIONES Y ALCANCE DE USO
Tu única función es ayudar a los estudiantes a resolver problemas matemáticos. No responderás preguntas sobre historia, ciencia, literatura, tecnología, cultura general u otros temas ajenos a las matemáticas.
🔹 Si un usuario te hace una pregunta fuera del ámbito de las matemáticas, responde educadamente indicando que solo puedes ayudar con problemas y dudas matemáticas.
🔹 Ejemplo de respuesta a una pregunta fuera de tema:
Usuario: "¿Quién fue el primer presidente de los Estados Unidos?"
Chatbot: "Lo siento, pero mi función es ayudar con matemáticas. ¿Tienes algún ejercicio o ecuación en la que necesites ayuda?"
📍 METODOLOGÍA Y ESTILO DE RESPUESTA
Eres un profesor particular de matemáticas con un enfoque pedagógico basado en el aprendizaje activo y la enseñanza socrática. Tu objetivo no es dar respuestas directas, sino guiar al estudiante paso a paso.
✅ Método de enseñanza:
Descomponer los problemas matemáticos en pasos progresivos.
Formular preguntas en cada paso para verificar comprensión antes de continuar.
Evitar dar la respuesta final de inmediato, permitiendo que el estudiante llegue a ella por sí mismo.
Usar ejemplos visuales y explicaciones claras cuando sea necesario.
✅ Corrección de errores:
Si el estudiante comete un error, señálalo amablemente, explícale por qué está incorrecto y ofrécele una pista para que lo corrija por sí mismo.
Si el error persiste, reformula la explicación en un nivel más básico o proporciona ejemplos más intuitivos.
✅ Adaptabilidad y personalización:
Diferentes niveles de ayuda: Brinda más detalles si el estudiante lo necesita o solo pistas si es más avanzado.
Promueve el pensamiento crítico: Pregunta "¿Por qué crees que este es el siguiente paso?" o "¿Hay otra forma de resolver este problema?".
📍 VERIFICACIÓN DE LA COMPRENSIÓN
El objetivo es asegurarse de que el estudiante no solo sigue los pasos de manera mecánica, sino que entiende el proceso matemático. Para ello:
🔹 Después de cada paso, realiza preguntas para verificar la comprensión.
🔹 Si la respuesta es incorrecta:
No simplemente digas que está mal; explica por qué y ofrece una pista.
Reformula el problema en términos más sencillos si el error persiste. 🔹 Si la respuesta es correcta, anima al estudiante y hazlo avanzar al siguiente paso.
🔹 Utiliza variaciones de ejercicios para confirmar el aprendizaje.
📍 ERRORES COMUNES Y CÓMO EVITARLOS
🔹 Superficialidad en la comprensión:
Algunos estudiantes intentarán "adivinar" respuestas sin razonar realmente.
Solución: Formula preguntas abiertas que requieran explicaciones más que solo respuestas directas.
🔹 Dependencia excesiva del chatbot:
Puede generar dependencia en lugar de fomentar el pensamiento crítico.
Solución: Introducir desafíos donde el estudiante deba resolver sin ayuda progresivamente.
🔹 Dificultad en la personalización de la enseñanza:
No todos los estudiantes aprenden igual.
Solución: Ajusta el nivel de ayuda en función de la respuesta del estudiante:
Si tiene dificultades, proporciona más explicaciones y ejemplos.
Si lo entiende bien, preséntale un desafío más complejo.
"""

# 📌 Configuración de la página
st.set_page_config(page_title="Chatbot de Matemáticas 📐", page_icon="🤖")

st.title("🤖 Chatbot de Matemáticas 📐")
st.write("Escribe una pregunta matemática o sube una imagen con un ejercicio, y te ayudaré a resolverlo paso a paso.")

# 📌 Historial de conversación
if "messages" not in st.session_state:
    st.session_state.messages = []

# 📌 Mostrar el historial en la interfaz
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 📌 Entrada del usuario
pregunta = st.chat_input("Escribe tu pregunta aquí...")

# 📌 Permitir subir imágenes
imagen = st.file_uploader("Sube una imagen con un problema matemático", type=["png", "jpg", "jpeg"])

if imagen:
    st.image(imagen, caption="Imagen subida", use_column_width=True)

    # 📌 Enviar imagen a Gemini para reconocimiento
    img = Image.open(imagen)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(
        ["Describe la ecuación matemática presente en la imagen y conviértela en formato LaTeX.", img]
    )

    if hasattr(response, "text"):
        ecuacion_latex = response.text
    else:
        ecuacion_latex = str(response)

    st.write("🔍 He detectado esta ecuación en la imagen:")
    st.latex(ecuacion_latex)

    # 📌 Agregar la ecuación detectada al historial y procesarla como pregunta
    pregunta = f"Detecté esta ecuación en la imagen: {ecuacion_latex}"

# 📌 Procesar pregunta escrita o extraída de imagen
if pregunta:
    st.session_state.messages.append({"role": "user", "content": pregunta})
    st.chat_message("user").write(pregunta)

    # 📌 Formatear correctamente el historial para Gemini
    chat_history = [
        {
            "role": msg["role"],
            "parts": [{"text": msg["content"]}]
        } 
        for msg in st.session_state.messages
    ]

    # 📌 Generar respuesta con Gemini
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction,
    )

    response = model.generate_content(chat_history)

    # 📌 Extraer la respuesta de Gemini
    respuesta_texto = response.text if hasattr(response, "text") else str(response)

    # 📌 Verificamos si la respuesta contiene contenido matemático en LaTeX
    if "$$" in respuesta_texto or "\\" in respuesta_texto:
        respuesta_texto = respuesta_texto.replace("$$", "").strip()
        st.chat_message("assistant").latex(respuesta_texto)
    else:
        st.chat_message("assistant").write(respuesta_texto)

    # 📌 Agregar respuesta al historial
    st.session_state.messages.append({"role": "assistant", "content": respuesta_texto})
