import { Equipment, Tractor, Combine, Implement } from '../lib/mockApi';

interface EquipmentCardProps {
  equipment: Equipment;
}

export function EquipmentCard({ equipment }: EquipmentCardProps) {
  const isTractor = (eq: Equipment): eq is Tractor => eq.category === 'tractor';
  const isCombine = (eq: Equipment): eq is Combine => eq.category === 'combine';
  const isImplement = (eq: Equipment): eq is Implement => eq.category === 'implement';

  return (
    <div className="equipment-card">
      <div className="equipment-header">
        <h3>{equipment.make} {equipment.model}</h3>
        <span className="category-badge">{equipment.category}</span>
      </div>

      {equipment.series && (
        <p className="series">{equipment.series}</p>
      )}

      {equipment.description && (
        <p className="description">{equipment.description}</p>
      )}

      <div className="equipment-details">
        {equipment.year_start && (
          <div className="detail">
            <span className="label">Year:</span>
            <span className="value">
              {equipment.year_start}
              {equipment.year_end && ` - ${equipment.year_end}`}
            </span>
          </div>
        )}

        {isTractor(equipment) && equipment.pto_hp && (
          <div className="detail">
            <span className="label">PTO HP:</span>
            <span className="value">{equipment.pto_hp}</span>
          </div>
        )}

        {(isTractor(equipment) || isCombine(equipment)) && equipment.engine_hp && (
          <div className="detail">
            <span className="label">Engine HP:</span>
            <span className="value">{equipment.engine_hp}</span>
          </div>
        )}

        {isTractor(equipment) && equipment.transmission_type && (
          <div className="detail">
            <span className="label">Transmission:</span>
            <span className="value">{equipment.transmission_type}</span>
          </div>
        )}

        {isCombine(equipment) && equipment.grain_tank_capacity && (
          <div className="detail">
            <span className="label">Tank Capacity:</span>
            <span className="value">{equipment.grain_tank_capacity} bu</span>
          </div>
        )}

        {isCombine(equipment) && equipment.separator_type && (
          <div className="detail">
            <span className="label">Separator:</span>
            <span className="value">{equipment.separator_type}</span>
          </div>
        )}

        {isImplement(equipment) && equipment.working_width && (
          <div className="detail">
            <span className="label">Width:</span>
            <span className="value">{equipment.working_width} ft</span>
          </div>
        )}

        {isImplement(equipment) && equipment.hp_required_min && (
          <div className="detail">
            <span className="label">HP Required:</span>
            <span className="value">
              {equipment.hp_required_min}
              {equipment.hp_required_max && ` - ${equipment.hp_required_max}`}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
