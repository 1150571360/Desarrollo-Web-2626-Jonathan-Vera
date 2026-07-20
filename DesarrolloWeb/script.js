document.addEventListener("DOMContentLoaded", function () {
    const formProductos = document.getElementById("formProductos");
    const listaProductos = document.getElementById("listaProductos");
    const contadorProductos = document.getElementById("contadorProductos");
    const formContacto = document.getElementById("formContacto");
    let productos = [];

    // --- Funciones reutilizables ---
    function validarCampoTexto(campo, errorId, minLength, mensajeError, mensajeOk) {
        if (campo.value.trim().length < minLength) {
            campo.classList.add("is-invalid");
            campo.classList.remove("is-valid");
            document.getElementById(errorId).textContent = mensajeError;
            return false;
        } else {
            campo.classList.remove("is-invalid");
            campo.classList.add("is-valid");
            document.getElementById(errorId).textContent = mensajeOk;
            return true;
        }
    }

    function validarCorreo(campo, errorId) {
        const regexCorreo = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!regexCorreo.test(campo.value.trim())) {
            campo.classList.add("is-invalid");
            campo.classList.remove("is-valid");
            document.getElementById(errorId).textContent = "Ingrese un correo válido.";
            return false;
        } else {
            campo.classList.remove("is-invalid");
            campo.classList.add("is-valid");
            document.getElementById(errorId).textContent = "Correo válido.";
            return true;
        }
    }

    function mostrarAlerta(id) {
        const alerta = document.getElementById(id);
        alerta.classList.remove("d-none");
        setTimeout(() => alerta.classList.add("d-none"), 3000);
    }

    function mostrarProductos() {
        listaProductos.innerHTML = "";
        productos.forEach((item, index) => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.innerHTML = <strong>${item.nombre}</strong> - ${item.descripcion} (${item.categoria});

            const btn = document.createElement("button");
            btn.textContent = "Eliminar";
            btn.className = "btn btn-danger btn-sm";
            btn.addEventListener("click", function () {
                productos.splice(index, 1);
                mostrarProductos();
            });

            li.appendChild(btn);
            listaProductos.appendChild(li);
        });
        contadorProductos.textContent = "Total productos: " + productos.length;
    }

    // --- Eventos ---
    formProductos.addEventListener("submit", function (e) {
        e.preventDefault();

        const nombre = document.getElementById("nombreProducto");
        const descripcion = document.getElementById("descripcion");
        const categoria = document.getElementById("categoria");

        let valido = true;
        valido &= validarCampoTexto(nombre, "errorNombre", 3, "El nombre debe tener al menos 3 caracteres.", "Nombre válido.");
        valido &= validarCampoTexto(descripcion, "errordescripcion", 10, "La descripción debe tener al menos 10 caracteres.", "Descripción válida.");
        valido &= validarCampoTexto(categoria, "errorCategoria", 1, "Debe seleccionar una categoría.", "Categoría válida.");

        if (valido) {
            productos.push({ nombre: nombre.value, descripcion: descripcion.value, categoria: categoria.value });
            mostrarProductos();
            formProductos.reset();
            nombre.classList.remove("is-valid");
            descripcion.classList.remove("is-valid");
            categoria.classList.remove("is-valid");
            mostrarAlerta("alertaExito");
        } else {
            mostrarAlerta("alertaError");
        }
    });

    formContacto.addEventListener("submit", function (e) {
        e.preventDefault();

        const nombre = document.getElementById("nombreContacto");
        const correo = document.getElementById("correo");
        const asunto = document.getElementById("asunto");
        const mensaje = document.getElementById("mensaje");

        let valido = true;
        valido &= validarCampoTexto(nombre, "errorNombreContacto", 3, "El nombre debe tener al menos 3 caracteres.", "Nombre válido.");
        valido &= validarCorreo(correo, "errorCorreo");
        valido &= validarCampoTexto(asunto, "errorAsunto", 3, "El asunto debe tener al menos 3 caracteres.", "Asunto válido.");
        valido &= validarCampoTexto(mensaje, "errorMensaje", 10, "El mensaje debe tener al menos 10 caracteres.", "Mensaje válido.");

        if (valido) {
            alert("Formulario enviado correctamente ✅");
            formContacto.reset();
            nombre.classList.remove("is-valid");
            correo.classList.remove("is-valid");
            asunto.classList.remove("is-valid");
            mensaje.classList.remove("is-valid");
        }
    });
});