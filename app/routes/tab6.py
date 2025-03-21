from flask import Blueprint, render_template, request, jsonify
from collections import defaultdict
from db_connection import DatabaseConnection
import re

tab6_bp = Blueprint("tab6_bp", __name__, url_prefix="/tab6")

def get_resale_items(conn):
    query = """
       SELECT * FROM id_item_master
       WHERE LOWER(bin_location) = 'resale'
       ORDER BY last_contract_num, tag_id
    """
    return conn.execute(query).fetchall()

def tokenize_name(name):
    return re.split(r'\W+', name.lower())

def categorize_item(item):
    tokens = tokenize_name(item.get("common_name", ""))
    if any(word in tokens for word in ['tent', 'canopy', 'pole', 'hp', 'mid', 'end', 'navi']):
        return 'Tent Tops'
    elif any(word in tokens for word in ['table', 'chair', 'plywood', 'prong']):
        return 'Tables and Chairs'
    elif any(word in tokens for word in ['132', '120', '90', '108']):
        return 'Round Linen'
    elif any(word in tokens for word in ['90x90', '90x132', '60x120', '90x156', '54']):
        return 'Rectangle Linen'
    elif any(word in tokens for word in ['otc', 'machine', 'hotdog', 'nacho']):
        return 'Concession'
    else:
        return 'Other'

def subcategorize_item(category, item):
    tokens = tokenize_name(item.get("common_name", ""))
    if category == 'Tent Tops':
        if any(word in tokens for word in ['hp']):
            return 'HP Tents'
        elif any(word in tokens for word in ['ncp', 'nc', 'end', 'pole']):
            return 'Pole Tents'
        elif any(word in tokens for word in ['navi']):
            return 'Navi Tents'
        elif any(word in tokens for word in ['canopy']):
            return 'AP Tents'
        else:
            return item.get("common_name", "Other Tents")
    elif category == 'Tables and Chairs':
        if 'table' in tokens:
            return 'Tables'
        elif 'chair' in tokens:
            return 'Chairs'
        else:
            return item.get("common_name", "Other T&C")
    elif category == 'Round Linen':
        if '90' in tokens:
            return '90-inch Round'
        elif '108' in tokens:
            return '108-inch Round'
        elif '120' in tokens:
            return '120-inch Round'
        elif '132' in tokens:
            return '132-inch Round'
        else:
            return item.get("common_name", "Other Round Linen")
    elif category == 'Rectangle Linen':
        if '90x90' in tokens:
            return '90 Square'
        elif '54' in tokens:
            return '54 Square'
        elif '90x132' in tokens:
            return '90x132'
        elif '90x156' in tokens:
            return '90x156'
        elif '60x120' in tokens:
            return '60x120'
        else:
            return item.get("common_name", "Other Rectangle Linen")
    elif category == 'Concession':
        if 'frozen' in tokens:
            return 'Frozen Drink Machines'
        elif 'cotton' in tokens:
            return 'Cotton Candy Machines'
        elif 'sno' in tokens:
            return 'SnoKone Machines'
        elif 'hotdog' in tokens:
            return 'Hotdog Machines'
        elif 'cheese' in tokens:
            return 'Warmers'
        elif 'popcorn' in tokens:
            return 'Popcorn Machines'
        else:
            return item.get("common_name", "Other Concessions")
    else:
        return item.get("common_name", "Other Items")

@tab6_bp.route("/")
def show_tab6():
    print("Loading /tab6/ endpoint")
    with DatabaseConnection() as conn:
        rows = get_resale_items(conn)
    items = [dict(row) for row in rows]

    # Get filter parameters
    filter_common_name = request.args.get("common_name", "").lower().strip()
    filter_tag_id = request.args.get("tag_id", "").lower().strip()
    filter_last_contract = request.args.get("last_contract_num", "").lower().strip()
    filter_status = request.args.get("status", "").lower().strip()

    # Filter items
    filtered_items = items
    if filter_common_name:
        filtered_items = [item for item in filtered_items if filter_common_name in (item.get("common_name") or "").lower()]
    if filter_tag_id:
        filtered_items = [item for item in filtered_items if filter_tag_id in (item.get("tag_id") or "").lower()]
    if filter_last_contract:
        filtered_items = [item for item in filtered_items if filter_last_contract in (item.get("last_contract_num") or "").lower()]
    if filter_status:
        filtered_items = [item for item in filtered_items if filter_status in (item.get("status") or "").lower()]

    # Group by category
    category_map = defaultdict(list)
    for item in filtered_items:
        cat = categorize_item(item)
        category_map[cat].append(item)

    # Parent data (categories)
    parent_data = []
    sub_map = {}
    middle_map = {}
    expand_category = request.args.get('expand', None)
    selected_subcat = request.args.get('subcat', None)

    for category, item_list in category_map.items():
        total_amount = len(item_list)
        on_contract = sum(1 for item in item_list if item["status"] in ["Delivered", "On Rent"])

        # Subcategories for dropdown
        temp_sub_map = defaultdict(list)
        for item in item_list:
            subcat = subcategorize_item(category, item)
            temp_sub_map[subcat].append(item)
        sub_map[category] = {"subcategories": list(temp_sub_map.keys())}

        # Middle child: Populate for first subcat or selected subcat
        subcat_to_show = selected_subcat if selected_subcat in temp_sub_map else list(temp_sub_map.keys())[0] if temp_sub_map else None
        if subcat_to_show:
            cat_items = temp_sub_map[subcat_to_show]
            common_name_map = defaultdict(list)
            for item in cat_items:
                common_name = item.get("common_name", "Unknown")
                common_name_map[common_name].append(item)
            middle_map[category] = [
                {"common_name": name, "total": len(items)}
                for name, items in common_name_map.items()
            ]

        parent_data.append({
            "category": category,
            "total_amount": total_amount,
            "on_contract": on_contract
        })

    parent_data.sort(key=lambda x: x["category"])

    return render_template(
        "tab6.html",
        parent_data=parent_data,
        middle_map=middle_map,
        sub_map=sub_map,
        expand_category=expand_category,
        selected_subcat=selected_subcat,
        filter_common_name=filter_common_name,
        filter_tag_id=filter_tag_id,
        filter_last_contract=filter_last_contract,
        filter_status=filter_status
    )

@tab6_bp.route("/subcat_data", methods=["GET"])
def subcat_data():
    print("Hit /tab6/subcat_data endpoint")
    category = request.args.get('category')
    subcat = request.args.get('subcat')
    common_name = request.args.get('common_name')
    page = int(request.args.get('page', 1))
    per_page = 20

    with DatabaseConnection() as conn:
        rows = get_resale_items(conn)
    items = [dict(row) for row in rows]

    # Apply filters from query params
    filter_common_name = request.args.get("common_name_filter", "").lower().strip()
    filter_tag_id = request.args.get("tag_id", "").lower().strip()
    filter_last_contract = request.args.get("last_contract_num", "").lower().strip()
    filter_status = request.args.get("status", "").lower().strip()

    filtered_items = items
    if filter_common_name:
        filtered_items = [item for item in filtered_items if filter_common_name in (item.get("common_name") or "").lower()]
    if filter_tag_id:
        filtered_items = [item for item in filtered_items if filter_tag_id in (item.get("tag_id") or "").lower()]
    if filter_last_contract:
        filtered_items = [item for item in filtered_items if filter_last_contract in (item.get("last_contract_num") or "").lower()]
    if filter_status:
        filtered_items = [item for item in filtered_items if filter_status in (item.get("status") or "").lower()]

    category_items = [item for item in filtered_items if categorize_item(item) == category]
    subcat_items = [item for item in category_items if subcategorize_item(category, item) == subcat]
    
    # Filter by specific common_name if provided
    if common_name:
        subcat_items = [item for item in subcat_items if item.get("common_name", "Unknown") == common_name]

    total_items = len(subcat_items)
    total_pages = (total_items + per_page - 1) // per_page
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    end = start + per_page
    paginated_items = subcat_items[start:end]

    print(f"AJAX: Category: {category}, Subcategory: {subcat}, Common Name: {common_name}, Total Items: {total_items}, Page: {page}")

    return jsonify({
        "items": [{
            "tag_id": item["tag_id"],
            "common_name": item["common_name"],
            "date_last_scanned": item.get("date_last_scanned", "N/A"),
            "last_scanned_by": item.get("last_scanned_by", "Unknown")
        } for item in paginated_items],
        "total_items": total_items,
        "total_pages": total_pages,
        "current_page": page
    })