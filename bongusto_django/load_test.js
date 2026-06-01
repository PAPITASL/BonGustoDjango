import http from 'k6/http';
import { sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 50 },   // Calentamiento
        { duration: '30s', target: 100 },  // Primer escalon real
        { duration: '30s', target: 150 },  // Empieza a exigir mas al backend
        { duration: '30s', target: 200 },
        { duration: '30s', target: 250 },
        { duration: '30s', target: 300 },  // Limite que queremos medir
        { duration: '10s', target: 0 },    // Enfriamiento
    ],
    thresholds: {
        http_req_failed: ['rate<0.05'],
    },
};

export default function () {

    http.get('http://127.0.0.1:8010/api/menus/');

    sleep(1);         // pausa de 1s entre peticiones

}

/* Opcional (muy recomendado): añadir checks y thresholds:
 */
/* import http from 'k6/http';

import { sleep, check } from 'k6';

export const options = {

    vus: 20,

    duration: '30s',

    thresholds: {

        http_req_duration: ['p(95)<200'], // 95% de las peticiones < 200 ms

        http_req_failed: ['rate<0.01'],   // < 1% de fallos

    },

};



export default function () {

    const res = http.get('http://127.0.0.1:8000/');

    check(res, {

        'status 200': r => r.status === 200,

    });

    sleep(1);

} */
