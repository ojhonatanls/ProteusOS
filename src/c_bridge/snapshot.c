#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/stat.h>
#include <dirent.h>

// Função para gerar um ID de snapshot (ex: snapshot_20240820_120000_alpine)
static char* generate_snapshot_id(const char* base_image) {
    time_t t = time(NULL);
    struct tm tm = *localtime(&t);
    char* snapshot_id = malloc(256);
    if (snapshot_id == NULL) return NULL;
    sprintf(snapshot_id, "snapshot_%04d%02d%02d_%02d%02d%02d_%s",
            tm.tm_year + 1900, tm.tm_mon + 1, tm.tm_mday,
            tm.tm_hour, tm.tm_min, tm.tm_sec,
            base_image);
    return snapshot_id;
}

// Função Python: snapshot_build(base_image)
static PyObject* py_snapshot_build(PyObject* self, PyObject* args) {
    const char* base_image;
    if (!PyArg_ParseTuple(args, "s", &base_image)) {
        return NULL;
    }

    char* snapshot_id = generate_snapshot_id(base_image);
    if (snapshot_id == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to generate snapshot ID");
        return NULL;
    }

    // Simula a criação do snapshot (aqui você pode adicionar a lógica real)
    printf("   Construindo imagem base '%s' (C)...\n", base_image);
    printf("   Snapshot gerado: %s\n", snapshot_id);

    PyObject* result = PyUnicode_FromString(snapshot_id);
    free(snapshot_id);
    return result;
}

// Função Python: snapshot_list()
static PyObject* py_snapshot_list(PyObject* self, PyObject* args) {
    // Simula listagem de snapshots (pode ser expandida)
    PyObject* list = PyList_New(0);
    PyList_Append(list, PyUnicode_FromString("snapshot_20240820_120000_alpine"));
    PyList_Append(list, PyUnicode_FromString("snapshot_20240820_120001_debian"));
    return list;
}

// Definição dos métodos do módulo
static PyMethodDef SnapshotMethods[] = {
    {"build", py_snapshot_build, METH_VARARGS, "Build a new snapshot."},
    {"list", py_snapshot_list, METH_VARARGS, "List all snapshots."},
    {NULL, NULL, 0, NULL}
};

// Definição do módulo
static struct PyModuleDef snapshotmodule = {
    PyModuleDef_HEAD_INIT,
    "snapshot",
    NULL,
    -1,
    SnapshotMethods
};

// Função de inicialização do módulo
PyMODINIT_FUNC PyInit_snapshot(void) {
    return PyModule_Create(&snapshotmodule);
}
