#!/usr/bin/env python3
"""
MUD Analyzer Web GUI
Web-based interface for MUD Analyzer using Flask
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from rest_client import MUDAnalyzerClient, MUDAnalyzerClientError
import json
import os

app = Flask(__name__)

# Configuration
API_URL = "http://localhost:8000"
rest_client = None


def get_client():
    """Get or create REST API client"""
    global rest_client
    if rest_client is None:
        rest_client = MUDAnalyzerClient(API_URL)
    return rest_client


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html', api_url=API_URL)


@app.route('/api/search', methods=['POST'])
def search():
    """Search endpoint"""
    try:
        data = request.json
        query = data.get('query', '').strip()
        entity_type = data.get('entity_type', 'all')
        limit = int(data.get('limit', 50))
        
        if not query:
            return jsonify({'error': 'Query is required'}), 400
        
        client = get_client()
        
        if entity_type == 'object':
            results = client.search_objects(query, limit=limit)
        elif entity_type == 'mobile':
            results = client.search_mobiles(query, limit=limit)
        else:
            results = client.search(query, limit=limit)
        
        # Convert results to dict format
        results_data = [
            {
                'vnum': r.vnum,
                'name': r.name,
                'zone': r.zone,
                'entity_type': r.entity_type
            }
            for r in results
        ]
        
        return jsonify({
            'success': True,
            'count': len(results_data),
            'results': results_data
        })
        
    except MUDAnalyzerClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/zone/<int:zone_num>', methods=['GET'])
def get_zone(zone_num):
    """Get zone information"""
    try:
        client = get_client()
        zone_info = client.get_zone(zone_num)
        
        return jsonify({
            'success': True,
            'data': zone_info
        })
        
    except MUDAnalyzerClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/object/<int:vnum>', methods=['GET'])
def get_object(vnum):
    """Get object details"""
    try:
        client = get_client()
        obj_info = client.get_object(vnum)
        
        return jsonify({
            'success': True,
            'data': obj_info
        })
        
    except MUDAnalyzerClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mobile/<int:vnum>', methods=['GET'])
def get_mobile(vnum):
    """Get mobile details"""
    try:
        client = get_client()
        mob_info = client.get_mobile(vnum)
        
        return jsonify({
            'success': True,
            'data': mob_info
        })
        
    except MUDAnalyzerClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/assemblies', methods=['POST'])
def find_assemblies():
    """Find item assemblies"""
    try:
        data = request.json
        obj_vnum = int(data.get('obj_vnum', 0))
        limit = int(data.get('limit', 50))
        
        if obj_vnum <= 0:
            return jsonify({'error': 'Valid VNUM is required'}), 400
        
        client = get_client()
        assemblies = client.find_assemblies(obj_vnum, limit=limit)
        
        return jsonify({
            'success': True,
            'data': assemblies
        })
        
    except MUDAnalyzerClientError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def status():
    """Check API status"""
    try:
        client = get_client()
        # Try a simple request
        try:
            client.get_zones(limit=1)
            return jsonify({
                'connected': True,
                'api_url': API_URL
            })
        except:
            return jsonify({
                'connected': False,
                'api_url': API_URL,
                'error': 'Cannot reach API server'
            })
    except Exception as e:
        return jsonify({
            'connected': False,
            'api_url': API_URL,
            'error': str(e)
        })


if __name__ == '__main__':
    print("Starting MUD Analyzer Web GUI...")
    print("Open http://localhost:5000 in your browser")
    app.run(debug=True, port=5000)
