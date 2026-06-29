document.addEventListener("DOMContentLoaded", function () {
    const formulario = document.getElementById("miFormulario");
    const lista = document.getElementById("listaRegistros");
    const contador = document.getElementById("contador");

    let registros = [];

    formulario.addEventListener("submit", function (e) {
        e.preventDefault();

        const dato = document.getElementById("campoTexto").value;

        if (dato.trim() !== "") {
            registros.push(dato);
            mostrarRegistros();
            formulario.reset();
        }
    });

    function mostrarRegistros() {
        lista.innerHTML = "";
        registros.forEach((item, index) => {
            const li = document.createElement("li");
            li.textContent = item;
            li.className = "list-group-item d-flex justify-content-between align-items-center";

            const btn = document.createElement("button");
            btn.textContent = "Eliminar";
            btn.className = "btn btn-danger btn-sm";
            btn.onclick = function () {
                registros.splice(index, 1);
                mostrarRegistros();
            };

            li.appendChild(btn);
            lista.appendChild(li);
        });

        contador.textContent = "Total registros: " + registros.length;
    }
});




document.addEventListener("DOMContentLoaded", function () {
    // --- Código de la primera sección dinámica ---
    const formulario = document.getElementById("miFormulario");
    const lista = document.getElementById("listaRegistros");
    const contador = document.getElementById("contador");
    let registros = [];

    formulario.addEventListener("submit", function (e) {
        e.preventDefault();
        const dato = document.getElementById("campoTexto").value;
        if (dato.trim() !== "") {
            registros.push(dato);
            mostrarRegistros();
            formulario.reset();
        }
    });

    function mostrarRegistros() {
        lista.innerHTML = "";
        registros.forEach((item, index) => {
            const li = document.createElement("li");
            li.textContent = item;
            li.className = "list-group-item d-flex justify-content-between align-items-center";

            const btn = document.createElement("button");
            btn.textContent = "Eliminar";
            btn.className = "btn btn-danger btn-sm";
            btn.onclick = function () {
                registros.splice(index, 1);
                mostrarRegistros();
            };

            li.appendChild(btn);
            lista.appendChild(li);
        });
        contador.textContent = "Total registros: " + registros.length;
    }

    // --- Código del formulario de productos ---
    const formProductos = document.getElementById("formProductos");
    const listaProductos = document.getElementById("listaProductos");
    const contadorProductos = document.getElementById("contadorProductos");
    let productos = [];

    formProductos.addEventListener("submit", function (e) {
        e.preventDefault();
        const nombre = document.getElementById("nombreProducto").value;
        const descripcion = document.getElementById("descripcion").value;
        const categoria = document.getElementById("categoria").value;

        // Validación dinámica
if (nombre.trim() === "") {
    document.getElementById("errorNombre").textContent = "El nombre es obligatorio.";
} else {
    document.getElementById("errorNombre").textContent = "";
}

if (descripcion.trim() === "") {
    document.getElementById("errorDescripcion").textContent = "La descripción es obligatoria.";
} else {
    document.getElementById("errorDescripcion").textContent = "";
}

if (categoria.trim() === "") {
    document.getElementById("errorCategoria").textContent = "La categoría es obligatoria.";
} else {
    document.getElementById("errorCategoria").textContent = "";
}

// Solo guardar si todo está correcto
if (nombre.trim() !== "" && descripcion.trim() !== "" && categoria.trim() !== "") {
    productos.push({ nombre, descripcion, categoria });
    mostrarProductos();
    formProductos.reset();
}
    });

    function mostrarProductos() {
        listaProductos.innerHTML = "";
        productos.forEach((item, index) => {
            const li = document.createElement("li");
            li.className = "list-group-item d-flex justify-content-between align-items-center";
            li.innerHTML = `<strong>${item.nombre}</strong> - ${item.descripcion} (${item.categoria})`;

            const btn = document.createElement("button");
            btn.textContent = "Eliminar";
            btn.className = "btn btn-danger btn-sm";
            btn.onclick = function () {
                productos.splice(index, 1);
                mostrarProductos();
            };

            li.appendChild(btn);
            listaProductos.appendChild(li);
        });
        contadorProductos.textContent = "Total productos: " + productos.length;
    }
});