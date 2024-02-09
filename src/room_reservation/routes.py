from flask import Blueprint, jsonify, request
from .database import db
from .models import Chambre, Reservation
from datetime import datetime

main = Blueprint('main', __name__)

##1
@main.route('/api/chambres/disponibles', methods=['GET'])
def chambres_disponibles():
    date_arrivee = request.args.get('date_arrivee')
    date_depart = request.args.get('date_depart')
    date_arrivee = datetime.strptime(date_arrivee, '%Y-%m-%d')
    date_depart = datetime.strptime(date_depart, '%Y-%m-%d')
    chambres = Chambre.query.all()
    chambres_disponibles = []

    for chambre in chambres:
        reservation = Reservation.query.filter(
            Reservation.id_chambre == chambre.id,
            Reservation.date_depart > date_arrivee,
            Reservation.date_arrivee < date_depart
        ).first()

        if not reservation:
            chambres_disponibles.append(chambre)

    return jsonify([{'id': chambre.id, 'numero': chambre.numero, 'type': chambre.type, 'prix': chambre.prix} for chambre in chambres_disponibles]), 200


##2
@main.route('/api/reservations', methods=['POST'])
def chambre_reservation():
    data = request.get_json()
    id_client = data.get('id_client')
    id_chambre = data.get('id_chambre')
    date_arrivee = data.get('date_arrivee')
    date_depart = data.get('date_depart')

    reservation = Reservation.query.filter(
        Reservation.id_chambre == id_chambre,
        Reservation.date_depart > date_arrivee,
        Reservation.date_arrivee < date_depart
    ).first()

    if reservation:
        return jsonify({"success": False, "message": "La chambre n est pas disponible pour les dates demandees"}), 400
    
    else:
        new_reservation = Reservation(
            id_client=id_client,
            id_chambre=id_chambre,
            date_arrivee=date_arrivee,
            date_depart=date_depart,
            statut="Reservee"
        )
        db.session.add(new_reservation)
        db.session.commit()
        return jsonify({"success": True, "message": "Reservation cree avec succes"}), 201



##3
@main.route('/api/reservations/<id>', methods=['DELETE'])
def annuler_reservation(id):
    reservation = Reservation.query.get(id)

    if not reservation:
        return jsonify({"success": False, "message": "Reservation non trouvee"}), 404

    db.session.delete(reservation)
    db.session.commit()

    return jsonify({"success": True, "message": "Reservation annulee avec succes"}), 200

        
##4
@main.route('/api/chambres', methods=['POST'])
def creation_chambre():
    data = request.get_json()

    chambre = Chambre.query.filter_by(numero = data.get('numero')).first()
    try:
        if chambre:
            return jsonify({ 
                "success": False, 
                "message": "Chambre existante"
            }), 400
        elif not chambre:
            new_chambre = Chambre(
                numero = data.get('numero'),
                type = data.get('type'),
                prix = data.get('prix')
            )
            db.session.add(new_chambre)
            db.session.commit()
            return jsonify({ 
                "success": True, 
                "message": "Chambre ajoutee avec succes"
            }), 201
    except:
        return jsonify({ 
            "success": False, 
            "message": "Chambre non ajoutee"
        }), 400



@main.route('/api/chambres/<id>', methods=['PUT'])
def maj_chambre(id):
    data = request.get_json()

    chambre = Chambre.query.get(id)
    if not chambre:
        return jsonify({ 
            "success": False, 
            "message": "Chambre non trouvee"
        }), 404

    chambre.numero = data.get('numero')
    chambre.type = data.get('type')
    chambre.prix = data.get('prix')

    try:
        db.session.commit()
        return jsonify({ 
            "success": True, 
            "message": "Chambre mise a jour avec succes"
        }), 200
    except:
        return jsonify({ 
            "success": False, 
            "message": "La mise a jour de la chambre a echoue"
        }), 400

@main.route('/api/chambres/<id>', methods=['DELETE'])
def supprimer_chambre(id):
    chambre = Chambre.query.get(id)
    if not chambre:
        return jsonify({ 
            "success": False, 
            "message": "Chambre non trouvee"
        }), 404

    try:
        db.session.delete(chambre)
        db.session.commit()
        return jsonify({ 
            "success": True, 
            "message": "Chambre supprimee avec succes"
        }), 200
    except:
        return jsonify({ 
            "success": False,
            "message": "La suppression de la chambre a echoue"
        }), 400

  

